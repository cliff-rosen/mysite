import pinecone
import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
import local_secrets as secrets
import conf

PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
MODEL = "text-embedding-ada-002"
INDEX_NAME = "main-index-2"
TEMPERATURE = .4
TOP_K = 10
MAX_CHUNKS_TOKEN_COUNT = 2500
WORDS_TO_TOKENS = 1 / .7

print("chunk_service initing AI and vector db")
pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)
openai.api_key = OPENAI_API_KEY


def ge(text):
    embedding_model = MODEL
    return get_embedding(
        text,
        engine=embedding_model
    )

# retrieve TOP_K embedding matches to query embedding
# return as dict {id: {"id": id, "score": score, "metadata": metadata}}
def get_chunks_from_embedding(domain_id, query_embedding, top_k=TOP_K):
    print("getting matches")
    matches = index.query(
        top_k=top_k,
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


# mutate chunks by adding {"uri": uri, "text", text} to each value dict
# chunks is dict where
#   key is chunk_id, and value is obj with score, text
def set_chunk_text_from_ids(chunks):
    print("getting chunk text")

    ids = list(chunks.keys())
    print("-----------")
    print("chunk ids:", ", ".join(ids))
    print("-----------")
    rows = db.get_document_chunks_from_ids(ids)
    for row in rows:
        doc_chunk_id = row["doc_chunk_id"]
        chunk_text = row["chunk_text"]
        doc_uri = row["doc_uri"]
        print(f"id: {doc_chunk_id}, text: {chunk_text[:20]}")
        chunks[str(doc_chunk_id)]["uri"] = doc_uri
        chunks[str(doc_chunk_id)]["text"] = chunk_text


# chunks dict: {id: {"id": id, "score": score, "text", text}}
def get_context_for_prompt(chunks, max_chunks_token_count = MAX_CHUNKS_TOKEN_COUNT):
    context = ""
    chunks_token_count = 0
    chunks_used_count = 0

    print('get_context_for_prompt using max token count of', max_chunks_token_count)

    for id, chunk in sorted(chunks.items(), key=lambda item: item[1]["score"], reverse = True):
        tokens_in_chunk = len(chunk['text'].split()) * WORDS_TO_TOKENS
        if chunks_token_count + tokens_in_chunk > max_chunks_token_count:
            print('context max size reached', id, chunks_token_count)
            break
        context = context + chunk['text'] + '\n\n'
        chunks_used_count += 1
        chunks_token_count += tokens_in_chunk
    print('chunks used:', chunks_used_count)

    if context:
        return '<START OF CONTEXT>\n' + context.strip() + '\n<END OF CONTEXT>'
    else:
        return ''
