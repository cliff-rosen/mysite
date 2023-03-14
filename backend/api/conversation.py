import pinecone
import openai
from openai.embeddings_utils import get_embedding
import logging
import traceback
from db import local_db as db
import local_secrets as secrets
from utils.utils import make_new_conversation_id

logger = logging.getLogger()

OPENAI_API_KEY = secrets.OPENAI_API_KEY
TEMPERATURE=.4
PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
MODEL = "text-embedding-ada-002"
INDEX_NAME = "main-index-2"
TEMPERATURE=.4
TOP_K=10

print("conversation initing AI and vector db")
pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)
openai.api_key = OPENAI_API_KEY


def create_prompt(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message    
    ):
    prompt=""

    try:
        conversation_history = sorted(conversation_history, key=lambda item: item["userMessageTimeStamp"])
        conversation_history_text = ""
        for entry in conversation_history:
            print("message", user_role_name + ': ' + entry['userMessage'])
            conversation_history_text += \
                user_role_name + ': ' + entry['userMessage'] + '\n' \
                + bot_role_name + ': ' + entry['response'] + '\n\n'

        prompt = prompt_header.strip() + '\n\n' \
            + bot_role_name + ': ' + initial_message.strip() + '\n\n' \
            + conversation_history_text.strip() + '\n\n' \
            + user_role_name + ': ' + user_message.strip() + '\n'\
            + bot_role_name + ': '
    except Exception as e:
        err_message = traceback.format_exc()
        logger.error('create_prompt: ' + err_message)
        #raise(e)

    return prompt


def query_model(prompt, stop_token, max_tokens, temperature):
    #model = 'gpt-3.5-turbo'
    model = 'text-davinci-003'
    print("prompt size: ", len(prompt), len(prompt.split()) )
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
        db.insert_conversation(conversation_id, 1, 30, conversation_text)
    except Exception as e:
        print('insert_conversation error: ', e)
        logger.error('insert_conversation error: ' + str(e))


def get_response(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message,
        max_tokens,
        temperature    
    ):
    logger.info('conversation.get_response')

    print("creating prompt")
    prompt = create_prompt(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message
    )
    logger.debug('Prompt:\n' + prompt)
    if not prompt:
        return {"status": "BAD_REQUEST"}

    print("querying model")
    response = query_model(prompt, user_role_name + ':', max_tokens, temperature)

    conversation_text = prompt + response
    insert_conversation('NA', 1, 30, conversation_text)

    return {"status": "SUCCESS", "response": response }


