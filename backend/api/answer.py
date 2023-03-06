import pinecone
import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
import local_secrets as secrets
from utils import make_new_conversation_id
import conf


PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
MODEL = "text-embedding-ada-002"
INDEX_NAME = "main-index-2"
TEMPERATURE=.4
TOP_K=10
MAX_WORD_COUNT = 2000
STOP_TOKEN = "User:"

pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)
print("answer initing openai")
openai.api_key = OPENAI_API_KEY

def ge(text):
    embedding_model = MODEL
    return get_embedding(
        text,
        engine=embedding_model
    )

# retrieve TOP_K embedding matches to query embedding
# return as dict {id: {"id": id, "score": score, "metadata": metadata}}
def get_chunks_from_embedding(domain_id, query_embedding):
    print("getting matches")
    matches = index.query(
        top_k=TOP_K,
        include_values=True,
        include_metadata=True,
        vector=query_embedding,
           filter={'domain_id': domain_id}).matches
    print('length:', len(matches))
    if len(matches) > 0:
        res = {matches[i].id : {"id" : int(matches[i].id), "score" : matches[i].score, "metadata": matches[i].metadata} for i in range(len(matches))}
    else:
        res = {}
    return res

# retrieve text for all chunks
# return as dict {"id": text} in desc score
def get_chunk_text_from_ids(chunks):
    print("getting chunks with text")
    chunks_with_text = {}

    # add text property to chunks
    ids = list(chunks.keys())
    print("-----------")
    print("chunk ids:", ", ".join(ids))
    print("-----------")
    rows = db.get_document_chunks_from_ids(ids)
    for row in rows:
        doc_chunk_id = row["doc_chunk_id"]
        chunk_text = row["chunk_text"]
        doc_uri = row["doc_uri"]
        print(f"id: {doc_chunk_id}, title: {chunk_text[:20]}")
        chunks[str(doc_chunk_id)]["uri"] = doc_uri
        chunks[str(doc_chunk_id)]["text"] = chunk_text

    # add chunks to chunks_with_text until word_count grows too large
    word_count = 0
    for id, chunk in sorted(chunks.items(), key=lambda item: item[1]["score"], reverse = True):
        num_words_in_chunk = len(chunk["text"].split())
        print("words", num_words_in_chunk)
        if word_count + num_words_in_chunk > MAX_WORD_COUNT:
            break
        chunks_with_text[str(chunk["id"])] = chunk["text"]
        word_count = word_count + num_words_in_chunk

    print('word count', word_count)
    return chunks_with_text


def get_conversation_history_text(conversation_history):
    conversation_text = ""
    user = 'User'
    ai = 'Chatbot'
    for row in conversation_history:
        conversation_text += f"{user}: {row['query_text']}\n{ai}: {row['response_text']}\n\n"
    return conversation_text


def get_context_for_prompt(chunks_with_text):
    context = ""

    if chunks_with_text:
        ids = list(chunks_with_text.keys())
        chunks_text_arr = [chunks_with_text[str(id)] for id in ids]
        context = "\n\n".join(chunks_text_arr)

    if context:
        return '<START OF CONTEXT>\n' + context + '\n<END OF CONTEXT>'
    else:
        return ''


def create_prompt_1(conversation_history, initial_message,
                    query, initial_prompt, chunks_with_text):
    user_role = 'User: '
    bot_role = 'Assistant: '

    context_for_prompt = ""
    conversation_history_text = ""
    prompt = ""

    context_for_prompt = get_context_for_prompt(chunks_with_text)

    conversation_history_text = get_conversation_history_text(conversation_history)

    prompt = initial_prompt.strip() + '\n\n' \
        + context_for_prompt + '\n\n' \
        + bot_role + initial_message + '\n\n' \
        + conversation_history_text  \
        + user_role + query + '\n' \
        + bot_role

    return prompt


def query_model_1(prompt, temp):
    #model = 'gpt-3.5-turbo'
    words_to_avoid = ["13681", "1049", "30932", "6275"]
    logit_bias = {}
    for word in words_to_avoid:
        logit_bias[word] = -100

    model = 'text-davinci-003'
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
                    initial_prompt, chunks_with_text):
    messages = []

    # add system message
    context_for_prompt = get_context_for_prompt(chunks_with_text)
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
            query, initial_prompt, chunks_with_text, temp):

    print("creating prompt")
    prompt = create_prompt_1(conversation_history, initial_message, query, 
                             initial_prompt, chunks_with_text)

    print("querying model")
    return query_model_1(prompt, temp)


def query_2(conversation_history, initial_message,
            query, initial_prompt, chunks_with_text):

    print("creating prompt")
    messages = create_prompt_2(conversation_history, initial_message, 
                               query, initial_prompt, chunks_with_text)

    print("querying model")
    return query_model_2(messages)


def update_conversation_tables(domain_id, query,
                initial_prompt, initial_message,
                query_temp, conversation_id, conversation_history,
                response_text, chunks_with_text, chunks,
                user_id, use_new_model):
    
    prompt = create_prompt_1(conversation_history, initial_message,
                             query, initial_prompt, chunks_with_text)
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

    logger.log('Conversation:\n' + conversation_text)

    return conversation_id


def get_answer(conversation_id, domain_id, query, 
               initial_prompt, temp, user_id, use_new_model):
    use_context = False
    chunks = {}
    chunks_with_text = {}
    use_context = False
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
        print("getting query embedding")
        query_embedding = ge(query)

        print("getting chunks ids")
        chunks = get_chunks_from_embedding(domain_id, query_embedding)
        if not chunks:
            # FIX ME: reply doesn't include converation_id and conv tables not updated
            return {"answer": "No data found for query", "chunks": {}, "chunks_used_count": 0 }
        print("getting chunk text from ids")
        chunks_with_text = get_chunk_text_from_ids(chunks)

    if use_new_model:
        print("answering with new model")
        response = query_2(conversation_history, initial_message, 
                       query, initial_prompt, chunks_with_text)
    else:
        print("answering with old model")
        response = query_1(conversation_history, initial_message,
                           query, initial_prompt, chunks_with_text, temp)

    print("updating conversation tables")
    conversation_id = update_conversation_tables(domain_id, query, 
                                                initial_prompt, initial_message,
                                                temp, conversation_id, conversation_history,
                                                response, chunks_with_text, chunks,
                                                user_id, use_new_model)

    return {"conversation_id": conversation_id, "answer": response, "chunks": chunks, "chunks_used_count": len(list(chunks_with_text.keys())) }


