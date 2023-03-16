import pinecone
import openai
from openai.embeddings_utils import get_embedding
import logging
import traceback
from db import local_db as db
import local_secrets as secrets
from utils.utils import make_new_conversation_id
import utils.chunks_service as chunk
from api.errors import InputError

logger = logging.getLogger()

OPENAI_API_KEY = secrets.OPENAI_API_KEY
TEMPERATURE=.4
PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
MODEL = "text-embedding-ada-002"
INDEX_NAME = "main-index-2"
TEMPERATURE = .4
TOP_K = 20
MAX_TOKEN_COUNT = 4000
WORDS_TO_TOKENS = 1 / .7

print("conversation initing AI and vector db")
pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)
openai.api_key = OPENAI_API_KEY

def build_prompt(prompt_header, context_for_prompt, bot_role_name, initial_message,
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

def num_tokens(*args):
    token_count = 0
    for arg in args:
        token_count += len(arg.split()) * WORDS_TO_TOKENS
    print('num_tokens before context', int(token_count))
    return int(token_count)

def create_prompt(
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
    max_context_token_count = MAX_TOKEN_COUNT - prompt_token_count - max_tokens
    context_for_prompt = chunk.get_context_for_prompt(chunks, max_context_token_count)

    prompt = build_prompt(
                prompt_header, context_for_prompt, 
                bot_role_name, initial_message,
                conversation_history_text, user_role_name, user_message
                )

    return prompt


def query_model(prompt, stop_token, max_tokens, temperature):
    #model = 'gpt-3.5-turbo'
    model = 'text-davinci-003'
    print("prompt char count: %s, token count: %s " % (len(prompt), int(len(prompt.split()) * WORDS_TO_TOKENS)))
    try:
        response = openai.Completion.create(
            model=model,
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
        if res['use_context']:
            use_context = True

    print("handling chunk retrieval")
    if use_context:
        print("getting query embedding")
        query_embedding = chunk.ge(user_message)

        print("getting chunks ids")
        chunks = chunk.get_chunks_from_embedding(domain_id, query_embedding, TOP_K)
        if not chunks:
            raise Exception('No chunks found - check index')
        print("getting chunk text from ids")
        chunk.set_chunk_text_from_ids(chunks)
        logger.debug("chunks with text: " + str(chunks))

    print("creating prompt")
    prompt = create_prompt(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message,
        chunks,
        max_tokens
    )
    logger.debug('Prompt:\n' + prompt)
    if not prompt:
        return {"status": "BAD_REQUEST"}

    print("querying model")
    response = query_model(prompt, user_role_name + ':', max_tokens, temperature)

    print("storing conversation")
    conversation_text = prompt + response
    insert_conversation('NA', 1, domain_id, conversation_text)

    return {"status": "SUCCESS", "response": response, "context": chunks }


