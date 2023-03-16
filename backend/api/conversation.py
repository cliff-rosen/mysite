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


def get_conversation_history_text(conversation_history):
    conversation_text = ""
    user = 'User'
    ai = 'Assistant'
    try:
        for row in conversation_history:
            conversation_text += f"{user}: {row['userMessage']}\n{ai}: {row['response']}\n\n"
    except Exception as e:
        raise InputError('Bad conversationHistory record:' + str(conversation_history))
    return conversation_text


def create_prompt_text(conversation_history, initial_message,
                    query, initial_prompt, chunks):
    user_role = 'User: '
    bot_role = 'Assistant: '

    context_for_prompt = ""
    conversation_history_text = ""
    prompt = ""

    context_for_prompt = chunk.get_context_for_prompt(chunks, MAX_TOKEN_COUNT)

    conversation_history_text = get_conversation_history_text(conversation_history)

    prompt = initial_prompt.strip() + '\n\n' \
        + context_for_prompt + '\n\n' \
        + bot_role + initial_message + '\n\n' \
        + conversation_history_text  \
        + user_role + query + '\n' \
        + bot_role

    return prompt


def create_prompt_messages(
                        conversation_history, initial_message, query,
                        initial_prompt, chunks, max_tokens
                        ):
    messages = []

    # get context
    if chunks:
        context_for_prompt = ""        
        conversation_history_text = get_conversation_history_text(conversation_history)
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


def insert_conversation(conversation_id, user_id, domain_id, conversation_text):
    conversation_id = 'NA'
    try:
        db.insert_conversation(conversation_id, 1, domain_id, conversation_text)
    except Exception as e:
        print('insert_conversation error: ', e)
        logger.error('insert_conversation error: ' + str(e))


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
    prompt_text = create_prompt_text(conversation_history, initial_message,
                             user_message, prompt_header, chunks)
    conversation_text = prompt_text + response
    insert_conversation('NA', 1, domain_id, conversation_text)

    return {"status": "SUCCESS", "response": response, "prompt": prompt_text, "context": chunks }


