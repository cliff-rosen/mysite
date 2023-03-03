import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
import local_secrets as secrets
from logger import Logger
from utils import make_new_conversation_id
import conf

OPENAI_API_KEY = secrets.OPENAI_API_KEY
TEMPERATURE=.4

print("initing openai")
openai.api_key = OPENAI_API_KEY

def create_prompt(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message    
    ):

    conversation_history = sorted(conversation_history, key=lambda item: item["userMessageTimeStamp"])
    conversation_history_text = ""
    for entry in conversation_history:
        print("message", user_role_name + ': ' + entry['userMessage'])
        conversation_history_text += \
            user_role_name + ': ' + entry['userMessage'] + '\n' \
            + bot_role_name + ': ' + entry['response'] + '\n\n'

    prompt = prompt_header.strip() + '\n\n' \
        + bot_role_name + ': ' + initial_message.strip() + '\n\n' \
        + conversation_history_text.strip() \
        + user_role_name + ': ' + user_message.strip() + '\n'\
        + bot_role_name + ': '

    return prompt


def query_model(prompt, stop_token, temp):
    #model = 'gpt-3.5-turbo'
    model = 'text-davinci-003'
    print("prompt size: ", len(prompt), len(prompt.split()) )
    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=500,
            temperature=temp,
            stop=stop_token
        )
        return response["choices"][0]["text"].strip(" \n")
    except Exception as e:
        print("query_model ERROR: " + str(e))
        return("Sorry, an unexpected error occured.  Please try again.")


def get_response(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message    
    ):
    logger = Logger('api.log')

    print("creating prompt")
    prompt = create_prompt(
        prompt_header,
        initial_message,
        user_role_name,
        bot_role_name,
        conversation_history,
        user_message    
    )
    logger.log('Prompt:\n' + prompt)

    print("querying model")
    response = query_model(prompt, user_role_name + ':', TEMPERATURE)

    conversation_text = prompt + response
    db.insert_conversation('NA', 1, 30, conversation_text)

    return {"status": "SUCCESS", "response": response }


