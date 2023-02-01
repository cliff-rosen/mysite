import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
import sys
sys.path.append('db')
sys.path.append('polls')
import local_db as db
import local_secrets as secrets

"""

embedding length: 1536

Retrieve all documents for domain
For each document
    break into chunks
    for each chunk
        get embedding
        insert chunk with embedding into document_chunk table
"""

OPENAI_API_KEY = secrets.OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

def get_openai_embedding(text):
    embedding_model = "text-embedding-ada-002"
    return get_embedding(
        text,
        engine="text-embedding-ada-002"
    )

def get_all_docs_from_domain(domain_id):
    return db.get_all_documents(conn, domain_id)

def get_chunks_from_text(text, r):
    if not r:
        chunks_splitter = CharacterTextSplitter(        
            separator = "\n\n",
            chunk_size = 1000,
            chunk_overlap  = 200,
            length_function = len,
        )
    else:
        text = re.sub('\s+', ' ', text)
        chunks_splitter = RecursiveCharacterTextSplitter(        
            chunk_size = 1000,
            chunk_overlap  = 200,
            length_function = len,
        )
    chunks = chunks_splitter.split_text(text)
    return chunks

# runtime settings
domain_id = 3

# init
conn = db.get_connection()

# one to one creation of chunks with embeddings
# FIX ME: should be upsertChunk() and not insertChunk()
rows = get_all_docs_from_domain(domain_id).fetchall()
for row in rows:
    doc_id = row[0]
    uri = row[2]
    print("*********************************")
    print(uri)
    chunks = get_chunks_from_text(row[4], True)
    for chunk in chunks:
        #clean_chunk = re.sub('\s+', ' ', chunk)
        print(doc_id, chunk[:50])
        print("----------------------")
        embedding = get_openai_embedding(chunk)
        db.insert_document_chunk(conn, doc_id, chunk, embedding)

# cleanup
db.close_connection(conn)
