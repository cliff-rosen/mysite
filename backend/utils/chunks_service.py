import pinecone
import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
from utils.utils import num_tokens_from_string
import local_secrets as secrets
import conf

PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
EMBEDDING_MODEL = "text-embedding-ada-002"
COMPLETION_MODEL = 'text-davinci-003'
INDEX_NAME = "main-index-2"
TEMPERATURE = .4
TOP_K = 40
MAX_CHUNKS_TOKEN_COUNT = 2500


print("chunk_service initing AI and vector db")
pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)
openai.api_key = OPENAI_API_KEY

'''
chunks dict: 
    {
        "ID":  {
            "id": ID as int,
            "score": score as float,
            "text": text,
            "metadata": {
                "doc_chunk_id": 44743.0,
                "doc_id": 20657.0,
                "domain_id": 27.0                
            }
            "uri": uri
        }
    }
'''

def ge(text):
    return get_embedding(
        text,
        engine=EMBEDDING_MODEL
    )

# retrieve TOP_K embedding matches to query embedding
# return as dict {id: {"id": id, "score": score, "metadata": metadata}}
def get_chunks_from_embedding(domain_id, query_embedding, top_k=TOP_K):
    print("querying index")
    matches = index.query(
        top_k=top_k,
        include_values=True,
        include_metadata=True,
        vector=query_embedding,
           filter={'domain_id': domain_id}).matches
    print('  query retrieved %s results' % (len(matches)))
    if len(matches) > 0:
        res = {matches[i].id : {"id" : int(matches[i].id), "score" : matches[i].score, "metadata": matches[i].metadata} for i in range(len(matches))}
    else:
        res = {}
    return res


# mutate chunks by adding {"uri": uri, "text", text} to each value dict
# chunks is dict where
#   key is chunk_id, and value is obj with score, text
def set_chunk_text_from_ids(chunks):
    ids = list(chunks.keys())
    rows = db.get_document_chunks_from_ids(ids)
    for row in rows:
        doc_chunk_id = row["doc_chunk_id"]
        chunk_text = row["chunk_text"]
        doc_uri = row["doc_uri"]
        print(f"id: {doc_chunk_id}, text: {chunk_text[:20]}")
        chunks[str(doc_chunk_id)]["uri"] = doc_uri
        chunks[str(doc_chunk_id)]["text"] = chunk_text


def get_chunks_from_query(domain_id, user_message, top_k=TOP_K):
    chunks = {}

    print("getting query embedding")
    query_embedding = ge(user_message)

    print("getting chunks ids")
    chunks = get_chunks_from_embedding(domain_id, query_embedding, top_k)
    if not chunks:
        raise Exception('No chunks found - check index')

    print("getting chunk text from ids")
    set_chunk_text_from_ids(chunks)

    return chunks


def get_context_for_prompt(chunks, max_chunks_token_count = MAX_CHUNKS_TOKEN_COUNT):
    print('get_context_for_prompt using max token count of', max_chunks_token_count)
    context = ""
    chunks_token_count = 0
    chunks_used_count = 0

    for id, chunk in sorted(chunks.items(), key=lambda item: item[1]["score"], reverse=True):
        tokens_in_chunk = num_tokens_from_string(chunk['text'], COMPLETION_MODEL)
        if chunks_token_count + tokens_in_chunk > max_chunks_token_count:
            print(' chunk', id, 'too long to fit.  moving on.')
            chunks[id]['used'] = False
            continue
        context = context + chunk['text'] + '\n\n'
        chunks[id]['used'] = True
        chunks_used_count += 1
        chunks_token_count += tokens_in_chunk
    print('chunks provided: %s, chunks used: %s, tokens used: %s' % (len(chunks), chunks_used_count, int(chunks_token_count)))

    if context:
        return '<START OF CONTEXT>\n' + context.strip() + '\n<END OF CONTEXT>'
    else:
        return ''
