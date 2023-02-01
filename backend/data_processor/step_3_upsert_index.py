import pinecone
import json
import sys
sys.path.append('db')
sys.path.append('polls')
import local_db as db

PINECONE_API_KEY = "7484d7df-d798-4b27-90c7-0f0164e6744d"
INDEX_NAME = "main-index"

pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)

def upsert_index(doc_id, doc_chunk_id, vector_str):
    id_str = str(doc_chunk_id)
    vector_obj = json.loads(vector_str)
    metadata = {'domain_id': domain_id, "doc_id": doc_id, "doc_chunk_id": doc_chunk_id}
    upsert_response = index.upsert(vectors=[(id_str, vector_obj, metadata)])
    print("response: ", upsert_response)

def run():
    conn = db.get_connection()
    rows = db.get_all_document_chunks(conn, domain_id).fetchall()
    for row in rows:
        print("upserting: ", row[1], row[2][:20])
        upsert_index(row[0], row[1], row[2])
    db.close_connection(conn)

def fetch():
    res = index.fetch(ids=['3'])
    print(res['vectors']['3']['metadata'])

# runtime settings
domain_id = 2

print(index.describe_index_stats())
run()
