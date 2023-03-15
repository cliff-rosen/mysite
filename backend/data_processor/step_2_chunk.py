import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
import os
import sys
import sys
sys.path.append('.\..')
from db import local_db as db
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

MIN_CHUNK_LENGTH = 20
MAX_CHUNK_LENGTH = 1500

OPENAI_API_KEY = secrets.OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

def get_openai_embedding(text):
    embedding_model = "text-embedding-ada-002"
    return get_embedding(
        text,
        engine="text-embedding-ada-002"
    )

def get_all_docs_from_domain(conn, domain_id):
    return db.get_all_docs_from_domain(conn, domain_id)

def get_chunks_from_text(text, maker_type):
    if maker_type == "MAKER_2":
        return get_chunks_from_text_2(text)

    if maker_type == "CHAR":
        print('chunking with CharacterTextSplitter')
        chunks_splitter = CharacterTextSplitter(        
            #separator = "\n\n",
            separator = "\n",
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

# create fragments, which are chunks delimited by \n\n
# chunks are fragments concatenated until a fragment is min 20 words
def get_chunks_from_text_2(text):
    print("chunk maker 2")
    chunks = []
    fragments = []

    # clean input
    text = text.encode(encoding='ASCII',errors='ignore').decode()
    text.strip()
    #text = re.sub('\s{3,}', '\n\n', text)    

    # build array of fragments by nn
    fragments = text.split('\n\n')

    # add array elements until reaching an element with at least 20 words
    cur_chunk = ""
    for i, fragment in enumerate(fragments):
        cur_chunk = cur_chunk + '\n' + fragment
        if len(cur_chunk) > 1 and (len(fragment.split()) >= 20 or i + 1 == len(fragments)):
            cur_chunk = cur_chunk.strip()
            if len(cur_chunk) > MIN_CHUNK_LENGTH:
                chunks.append(cur_chunk)
            cur_chunk = ""

    return chunks

# runtime settings
#chunk_maker = "MAKER_2"
chunk_maker = "CHAR"
domain_id = 33

def run():
    # init
    conn = db.get_connection()

    # one to one creation of chunks with embeddings
    # FIX ME: should be upsertChunk() and not insertChunk()
    print("Retrieve documents for domain", domain_id)
    rows = get_all_docs_from_domain(conn, domain_id)
    print("Retrieved: ", len(rows))
    for doc_id, domain_id, uri, doc_title, doc_text in rows:
        print("***********************************************************")
        chunks = get_chunks_from_text(doc_text, chunk_maker)
        print(uri, chunks.length)
        for chunk in chunks:
            print(doc_id, chunk[:50])
            print("----------------------")
            embedding = get_openai_embedding(chunk[:MAX_CHUNK_LENGTH])
            db.insert_document_chunk(conn, doc_id, chunk, embedding)

    # cleanup
    db.close_connection(conn)

def write_to_file(text):
    directory = 'outputs'
    dest = 'chunks.txt'
    with open(os.path.join(directory, dest), 'a') as new_file:
        new_file.write(text)

def test_chunker():
    print("TEST: Retrieve documents for domain", domain_id)
    conn = db.get_connection()
    rows = get_all_docs_from_domain(conn, domain_id)
    db.close_connection(conn)

    for _doc_id, _domain_id, uri, _doc_title, doc_text in rows:
        print("***********************************************************")
        print(uri)
        chunks = get_chunks_from_text(doc_text, chunk_maker)
        for chunk in chunks:
            write_to_file(chunk + '\n==============\n')
            
#test_chunker()
run()

#####################################################
#clean_chunk = re.sub('\s+', ' ', chunk)