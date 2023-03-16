import pinecone
import openai
import logging
import traceback
from db import local_db as db
import local_secrets as secrets
from utils.utils import make_new_conversation_id, num_tokens_from_string
import utils.chunks_service as chunk
from api.errors import InputError

logger = logging.getLogger()

OPENAI_API_KEY = secrets.OPENAI_API_KEY
TEMPERATURE=.4
PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
INDEX_NAME = "main-index-2"
TEMPERATURE = .4
TOP_K = 40
COMPLETION_MODEL = 'gpt-4' #'text-davinci-003'
COMPLETION_MODEL_TIKTOKEN = 'text-davinci-003'
MAX_TOKEN_COUNT = 8000

print("conversation initing AI and vector db")
pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)
openai.api_key = OPENAI_API_KEY


def num_tokens(*args):
    token_count = 0
    text = ''
    for arg in args:
        text += arg
    token_count += num_tokens_from_string(text, COMPLETION_MODEL_TIKTOKEN)
    return int(token_count)


def build_prompt_OLD(prompt_header, context_for_prompt, bot_role_name, initial_message,
                conversation_history_text, user_role_name, user_message):
    if context_for_prompt:
        context_for_prompt = context_for_prompt + '\n\n'

    prompt = prompt_header.strip() + '\n\n' \
        + context_for_prompt \
        + bot_role_name + ': ' + initial_message.strip() + '\n\n' \
        + conversation_history_text \
        + user_role_name + ': ' + user_message.strip() + '\n'\
        + bot_role_name + ': '

    return prompt

def create_prompt_OLD(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message,
        chunks,
        max_tokens  
    ):
    prompt=""
    conversation_history_text = ""
    context_for_prompt = ""

    try:
        conversation_history = sorted(conversation_history, key=lambda item: item["userMessageTimeStamp"])
        for entry in conversation_history:
            print("message", user_role_name + ': ' + entry['userMessage'])
            conversation_history_text += \
                user_role_name + ': ' + entry['userMessage'] + '\n' \
                + bot_role_name + ': ' + entry['response'] + '\n\n'
    except Exception as e:
        err_message = traceback.format_exc()
        logger.warning('create_prompt error reading conversation history: ' + err_message)
        logger.warning('JSON: ' + str(conversation_history) )
        raise(InputError('Invalid input to create_prompt.  Suspect bad input JSON'))

    prompt_token_count = num_tokens(prompt_header, initial_message, conversation_history_text, user_message)
    print('tokens used by pre-context prompt: %s' % (prompt_token_count))
    max_context_token_count = MAX_TOKEN_COUNT - prompt_token_count - max_tokens
    context_for_prompt = chunk.get_context_for_prompt(chunks, max_context_token_count)

    prompt = build_prompt(
                prompt_header, context_for_prompt, 
                bot_role_name, initial_message,
                conversation_history_text, user_role_name, user_message
                )

    return prompt


def query_model_OLD(prompt, stop_token, max_tokens, temperature):
    print("prompt token count: %s" % (num_tokens(prompt)))
    try:
        response = openai.Completion.create(
            model=COMPLETION_MODEL,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop_token
        )
        return response["choices"][0]["text"].strip(" \n")
    except Exception as e:
        logger.error('conversation.query_model: ' + str(e))
        return("Sorry, an unexpected error occured.  Please try again.")


def insert_conversation(conversation_id, user_id, domain_id, conversation_text):
    conversation_id = 'NA'
    try:
        db.insert_conversation(conversation_id, 1, domain_id, conversation_text)
    except Exception as e:
        print('insert_conversation error: ', e)
        logger.error('insert_conversation error: ' + str(e))


def create_prompt_messages(
                        conversation_history, initial_message, query,
                        initial_prompt, chunks, max_tokens
                        ):
    messages = []

    # get context
    if chunks:
        context_for_prompt = ""        
        conversation_history_text = ""
        for entry in conversation_history:
            conversation_history_text += \
                'User: ' + entry['userMessage'] + '\n' \
                + 'Assistant:' + entry['response'] + '\n\n'
        prompt_token_count = num_tokens(initial_prompt, conversation_history_text, initial_message, query)
        print('tokens used by pre-context prompt: %s' % (prompt_token_count))
        max_context_token_count = MAX_TOKEN_COUNT - prompt_token_count - max_tokens
        context_for_prompt = chunk.get_context_for_prompt(chunks, max_context_token_count)
        if context_for_prompt:
            initial_prompt += '\n\n' + context_for_prompt

    # add system message
    messages.append({"role": "system", "content": initial_prompt})

    # add initial assistant message
    messages.append({"role": "assistant", "content": initial_message})

    # add user and assistant messages from history
    conversation_history = sorted(conversation_history, key=lambda item: item["userMessageTimeStamp"])    
    for row in conversation_history:
        messages.append({"role": "user", "content": row['userMessage']})        
        messages.append({"role": "assistant", "content": row['response']})   

    # add new user message
    messages.append({"role": "user", "content": query})

    return messages


def query_model(messages, max_tokens, temperature):
    completion = openai.ChatCompletion.create(
        model=COMPLETION_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
        )

    return completion.choices[0].message.content


def get_response(
        domain_id,
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message,
        max_tokens,
        temperature
    ):
    logger.info('conversation.get_response: ' + user_message)
    print('get_response -------------------------------->')
    use_context = False
    chunks = {}

    print("getting domain settings")
    if domain_id != 0:
        res = db.get_domain(domain_id)
        if not res:
            logger.warning('get_response got bad domain_id: ' + str(domain_id))
            raise InputError('Bad domain_id: ' + str(domain_id))
        if res['use_context']:
            use_context = True

    print("handling chunk retrieval")
    if use_context:
        chunk.set_chunks_from_query(domain_id, chunks, user_message, TOP_K)
        logger.debug("chunks with text: " + str(chunks))

    print("creating prompt")
    prompt_messages = create_prompt_messages(
        conversation_history,
        initial_message,
        user_message,
        prompt_header,
        chunks,
        max_tokens
    )
    logger.info('Prompt:\n' + str(prompt_messages))
    if not prompt_messages:
        return {"status": "BAD_REQUEST"}

    print("querying model")
    response = query_model(prompt_messages, max_tokens, temperature)

    print("storing conversation")
    #conversation_text = prompt + response
    #insert_conversation('NA', 1, domain_id, conversation_text)

    return {"status": "SUCCESS", "response": response, "prompt": "TBD", "context": chunks }


