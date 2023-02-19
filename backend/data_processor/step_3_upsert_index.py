import pinecone
import json
import sys
from db import local_db as db
import local_secrets as secrets

"""
TO DO:
log error if upsert response not {'upserted_count': 1}
upsert in batches

"""
PINECONE_API_KEY = secrets.PINECONE_API_KEY
INDEX_NAME = "main-index"

pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)

def upsert_index(doc_id, doc_chunk_id, vector_str):
    id_str = str(doc_chunk_id)
    vector_obj = json.loads(vector_str)
    metadata = {'domain_id': domain_id, "doc_id": doc_id, "doc_chunk_id": doc_chunk_id}
    upsert_response = index.upsert(vectors=[(id_str, vector_obj, metadata)])
    print("  response: ", upsert_response)

def run():
    print("Starting upsert for domain", domain_id)
    conn = db.get_connection()
    rows = db.get_document_chunks(conn, domain_id)
    cur_count = 1
    tot_count = len(rows)
    print("Total chunks to be upserted", tot_count)
    for row in rows:
        print("Processing ", cur_count, " of ", tot_count)
        doc_id = row['doc_id']
        doc_chunk_id = row['doc_chunk_id']
        chunk_embedding = row['chunk_embedding']
        print("  Upserting: ", doc_chunk_id, chunk_embedding[:20])
        upsert_index(doc_id, doc_chunk_id, chunk_embedding)
        cur_count = cur_count + 1
    db.close_connection(conn)

def fetch():
    res = index.fetch(ids=['3'])
    print(res['vectors']['3']['metadata'])

# runtime settings
domain_id = 29

print(index.describe_index_stats())
run()
