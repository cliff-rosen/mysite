import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
import local_secrets as secrets
from utils.utils import make_new_conversation_id
import conf
import utils.chunks_service as chunk


STOP_TOKEN = "User:"


def get_conversation_history_text(conversation_history):
    conversation_text = ""
    user = 'User'
    ai = 'Chatbot'
    for row in conversation_history:
        conversation_text += f"{user}: {row['query_text']}\n{ai}: {row['response_text']}\n\n"
    return conversation_text


def create_prompt_1(conversation_history, initial_message,
                    query, initial_prompt, chunks):
    user_role = 'User: '
    bot_role = 'Assistant: '

    context_for_prompt = ""
    conversation_history_text = ""
    prompt = ""

    context_for_prompt = chunk.get_context_for_prompt(chunks)

    conversation_history_text = get_conversation_history_text(conversation_history)

    prompt = initial_prompt.strip() + '\n\n' \
        + context_for_prompt + '\n\n' \
        + bot_role + initial_message + '\n\n' \
        + conversation_history_text  \
        + user_role + query + '\n' \
        + bot_role

    return prompt


def query_model_1(prompt, temp):
    model = 'text-davinci-003'
    words_to_avoid = ["13681", "1049", "30932", "6275"]
    logit_bias = {}
    for word in words_to_avoid:
        logit_bias[word] = -100

    print("prompt size: ", len(prompt), len(prompt.split()) )
    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=500,
            temperature=temp,
            logit_bias = {13681: -90},
            stop=STOP_TOKEN
        )
        return response["choices"][0]["text"].strip(" \n")
    except Exception as e:
        print("query_model ERROR: " + str(e))
        return("Sorry, an unexpected error occured.  Please try again.")


def create_prompt_2(conversation_history, initial_message, query,
                    initial_prompt, chunks):
    messages = []

    # add system message
    context_for_prompt = chunk.get_context_for_prompt(chunks)
    if context_for_prompt:
        initial_prompt += '\n\n' + context_for_prompt
    messages.append({"role": "system", "content": initial_prompt})

    # add initial assistant message
    messages.append({"role": "assistant", "content": initial_message})

    # add user and assistant messages from history
    for row in conversation_history:
        messages.append({"role": "user", "content": row['query_text']})        
        messages.append({"role": "assistant", "content": row['response_text']})   

    # add new user message
    messages.append({"role": "user", "content": query})

    return messages


def query_model_2(messages):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        logit_bias = {13681: -90}
        )

    return completion.choices[0].message.content


def query_1(conversation_history, initial_message,
            query, initial_prompt, chunks, temp):

    print("creating prompt")
    prompt = create_prompt_1(conversation_history, initial_message, query, 
                             initial_prompt, chunks)

    print("querying model")
    return query_model_1(prompt, temp)


def query_2(conversation_history, initial_message,
            query, initial_prompt, chunks):

    print("creating prompt")
    messages = create_prompt_2(conversation_history, initial_message, 
                               query, initial_prompt, chunks)

    print("querying model")
    return query_model_2(messages)


def update_conversation_tables(domain_id, query,
                initial_prompt, initial_message,
                query_temp, conversation_id, conversation_history,
                response_text, chunks,
                user_id, use_new_model):
    
    prompt = create_prompt_1(conversation_history, initial_message,
                             query, initial_prompt, chunks)
    if use_new_model:
        prompt = 'NEW MODEL\n' + prompt
    else:
        prompt = 'OLD MODEL\n' + prompt

    conversation_text = prompt + response_text + '\n'

    if conversation_id == 'NEW':
        conversation_id = make_new_conversation_id()
        db.insert_conversation(conversation_id, user_id, 
                               domain_id, conversation_text)
    else:
        db.update_conversation(conversation_id, conversation_text)

    response_chunk_ids = ', '.join(list(chunks.keys()))
    db.insert_query_log(domain_id, query, prompt, query_temp, response_text,
                        response_chunk_ids, user_id, conversation_id)

    #logger.log('Conversation:\n' + conversation_text)

    return conversation_id


def get_answer(conversation_id, domain_id, query, 
               initial_prompt, temp, user_id, use_new_model):
    print('get_answer -------------------------------->')
    use_context = False
    chunks = {}
    initial_message = conf.DEFAULT_INITIAL_MESSAGE
    conversation_history = []

    print("getting domain settings")
    res = db.get_domain(domain_id)
    if res['initial_conversation_message']:
        initial_message = res['initial_conversation_message']
    if res['use_context']:
        use_context = True

    print("getting conversation history")
    if conversation_id != 'NEW':
        conversation_history = db.get_conversation_history(conversation_id)
    
    print("handling chunk retrieval")
    if use_context:
        chunks = chunk.get_chunks_from_query(domain_id, query)
        if not chunks:
            # FIX ME: reply doesn't include converation_id and conv tables not updated
            return {"answer": "No data found for query", "chunks": {}, "chunks_used_count": 0 }
        print("getting chunk text from ids")

    if use_new_model:
        print("answering with new model")
        response = query_2(conversation_history, initial_message, 
                       query, initial_prompt, chunks)
    else:
        print("answering with old model")
        response = query_1(conversation_history, initial_message,
                           query, initial_prompt, chunks, temp)

    print("updating conversation tables")
    conversation_id = update_conversation_tables(domain_id, query, 
                                                initial_prompt, initial_message,
                                                temp, conversation_id, conversation_history,
                                                response, chunks,
                                                user_id, use_new_model)

    print('get_answer completed')
    return {"conversation_id": conversation_id, "answer": response, "chunks": chunks, "chunks_used_count": len(list(chunks.keys())) }


