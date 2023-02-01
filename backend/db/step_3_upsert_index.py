import pinecone
import json
import db

PINECONE_API_KEY = "7484d7df-d798-4b27-90c7-0f0164e6744d"
INDEX_NAME = "whc-site"

pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)

def upsert_index(id, vector_str, text):
    id_str = str(id)
    vector_obj = json.loads(vector_str)
    metadata = {'text-prefix': text[:20]}
    upsert_response = index.upsert(vectors=[(id_str, vector_obj, metadata)])
    print("response: ", upsert_response)

def run():
    conn = db.getConnection()
    rows = db.getAllDocumentChunks(conn).fetchall()
    for row in rows:
        upsert_index(row[0], row[3], row[2])
    db.closeConnection(conn)

def fetch():
    res = index.fetch(ids=['3'])
    print(res['vectors']['3']['metadata'])


print(index.describe_index_stats())
run()
