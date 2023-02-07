import pinecone
import openai
from openai.embeddings_utils import get_embedding
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import local_db as db
import local_secrets as secrets
import conf

PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
MODEL = "text-embedding-ada-002"
INDEX_NAME = "main-index"
TEMPERATURE=.4
TOP_K=10
MAX_WORD_COUNT = 2500

pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)

print("initing openai")
openai.api_key = OPENAI_API_KEY

def ge(text):
    print(OPENAI_API_KEY)
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

def create_prompt(question, chunks_with_text, prompt):
    ids = list(chunks_with_text.keys())
    chunks_text_arr = [chunks_with_text[str(id)] for id in ids]
    context = "".join(chunks_text_arr)
    #prompt = conf.PROMPT
    prompt = prompt.replace("<<CONTEXT>>", context)
    prompt = prompt.replace("<<QUESTION>>", question)
    return prompt

def query_model(prompt, temp):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        temperature=temp
    )
    return response["choices"][0]["text"].strip(" \n")

def log_result(domain_id, query_text, query_prompt, query_temp, response_text, chunks, user_id):
    response_chunk_ids = ', '.join(list(chunks.keys()))
    db.insert_query_log(domain_id, query_text, query_prompt, query_temp, response_text, response_chunk_ids, user_id)

def get_answer(domain_id, query, prompt_text, temp, user_id):

    print("getting query embedding")
    query_embedding = ge(query)

    print("getting chunks ids")
    chunks = get_chunks_from_embedding(domain_id, query_embedding)
    if not chunks:
        return {"answer": "no data", "chunks": {}, "chunks_used_count": 0 }

    print("getting chunk text from ids")
    chunks_with_text = get_chunk_text_from_ids(chunks)

    print("creating prompt")
    prompt = create_prompt(query, chunks_with_text, prompt_text)

    print("querying model")
    response = query_model(prompt, temp)

    log_result(domain_id, query, prompt, temp, response, chunks_with_text, user_id)

    return {"answer": response, "chunks": chunks, "chunks_used_count": len(list(chunks_with_text.keys())) }


