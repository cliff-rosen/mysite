import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
import local_secrets as secrets
from logger import Logger
from utils import make_new_conversation_id
import conf

OPENAI_API_KEY = secrets.OPENAI_API_KEY
TEMPERATURE=.4
STOP_TOKEN = "Patient:"

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
    prompt = "TBD"

    return prompt


def query_model(prompt, temp):
    #model = 'gpt-3.5-turbo'
    model = 'text-davinci-003'
    print("prompt size: ", len(prompt), len(prompt.split()) )
    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=500,
            temperature=temp,
            stop=STOP_TOKEN
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
    print(conversation_history)
    
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
    response = query_model(prompt, TEMPERATURE)

    #conversation_id = update_conversation_tables(domain_id, query, prompt, temp, response, chunks_with_text, user_id, conversation_id)

    return {"status": "SUCCESS", "response": response }


