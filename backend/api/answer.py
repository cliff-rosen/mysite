import pinecone
import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
import local_secrets as secrets
from logger import Logger
from utils import make_new_conversation_id
import conf

PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
MODEL = "text-embedding-ada-002"
INDEX_NAME = "main-index"
TEMPERATURE=.4
TOP_K=10
MAX_WORD_COUNT = 2000

pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)

print("initing openai")
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


def get_conversation_history(conversation_id):
    conversation_text = ""
    user = 'Patient'
    ai = 'Chatbot'
    rows = db.get_conversation_history(conversation_id)
    for row in rows:
        conversation_text += f"{user}: {row['query_text']}\n{ai}: {row['response_text']}\n\n"
    return conversation_text


def create_prompt(domain_id, conversation_id, query, initial_prompt, followup_prompt_template, chunks_with_text):
    prompt = ""
    conversation_history = ""
    context = ""

    if conversation_id != 'NEW':
        conversation_history = get_conversation_history(conversation_id)

    if chunks_with_text:
        ids = list(chunks_with_text.keys())
        chunks_text_arr = [chunks_with_text[str(id)] for id in ids]
        context = "\n\n".join(chunks_text_arr)

    followup_prompt = followup_prompt_template
    followup_prompt = followup_prompt.replace("<<CONTEXT>>", context)
    followup_prompt = followup_prompt.replace("<<QUESTION>>", query)

    prompt = initial_prompt + conversation_history + followup_prompt
    return prompt


def query_model(prompt, temp):
    print("prompt size: ", len(prompt), len(prompt.split()) )
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=temp
        )
        return response["choices"][0]["text"].strip(" \n")
    except Exception as e:
        print("query_model ERROR: " + str(e))
        return("Sorry, an unexpected error occured.  Please try again.")


def update_conversation_tables(
                domain_id, 
                query_text, prompt, query_temp,
                response_text, chunks, 
                user_id, conversation_id):
    conversation_text = prompt + response_text + '\n'
    if conversation_id == 'NEW':
        conversation_id = make_new_conversation_id()
        db.insert_conversation(conversation_id, user_id, domain_id, conversation_text)
    else:
        db.update_conversation(conversation_id, conversation_text)

    response_chunk_ids = ', '.join(list(chunks.keys()))
    db.insert_query_log(domain_id, query_text, prompt, query_temp, response_text, response_chunk_ids, user_id, conversation_id)

    return conversation_id


def get_answer(conversation_id, domain_id, query, prompt, temp, user_id):
    chunks = {}
    chunks_with_text = {}
    logger = Logger('api.log')

    initial_prompt = prompt #conf.DEFAULT_INITIAL_PROMPT
    followup_prompt_template = conf.DEFAULT_FOLLOWUP_PROMPT

    print("getting custom prompts")
    res = db.get_domain(domain_id)
    #if res['initial_prompt_template']:
    #    initial_prompt = res['initial_prompt_template']
    if res['followup_prompt_template']:
        followup_prompt_template = res['followup_prompt_template']

    print("getting query embedding")
    query_embedding = ge(query)

    print("handling chunk retrieval")
    if (followup_prompt_template.find("<<CONTEXT>>") > -1):
        print("getting chunks ids")
        chunks = get_chunks_from_embedding(domain_id, query_embedding)
        if not chunks:
            return {"answer": "No data found for query", "chunks": {}, "chunks_used_count": 0 }
        print("getting chunk text from ids")
        chunks_with_text = get_chunk_text_from_ids(chunks)

    print("creating prompt")
    #prompt = create_prompt(domain_id, prompt_template, conversation_id, query, chunks_with_text)
    prompt = create_prompt(domain_id, conversation_id, query, initial_prompt, followup_prompt_template, chunks_with_text)
    logger.log('Prompt:\n' + prompt)

    print("querying model")
    response = query_model(prompt, temp)

    conversation_id = update_conversation_tables(domain_id, query, prompt, temp, response, chunks_with_text, user_id, conversation_id)

    return {"answer": response, "chunks": chunks, "chunks_used_count": len(list(chunks_with_text.keys())), "conversation_id": conversation_id }


