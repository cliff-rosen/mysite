from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
import os
import sys
sys.path.append('db')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import local_db as db
import local_secrets as secrets

def get_chunks_from_text_2(text):
    print("chunker 2")
    chunks = []
    fragments = []

    # clean input
    text.strip()
    while text.find("\n\n\n") > -1:
        text = text.replace("\n\n\n", "\n\n")

    # built array of fragments by nn
    fragments = text.split('\n\n')

    # add array elements until reaching an element with at least 20 words
    cur_chunk = ""
    for i, fragment in enumerate(fragments):
        if len(fragment) > 1:
            if i > 0:
                cur_chunk = cur_chunk  + "\n"
            cur_chunk = cur_chunk + fragment
        if len(cur_chunk) > 1 and (len(fragment.split()) >= 20 or i + 1 == len(fragments)):
            chunks.append(cur_chunk.strip())
            cur_chunk = ""

    return chunks

# runtime settings
doc_id = 4333

text = db.get_document(doc_id)[0]["doc_text"]
with open("page.txt", 'w') as new_file:
    #clean_chunk = re.sub('\s+', ' ', chunk_text)
    #clean_chunk = clean_chunk.encode(encoding='ASCII',errors='ignore').decode()
    new_file.write(text)

chunks = get_chunks_from_text_2(text)
with open("new.txt", 'w') as new_file:
    for chunk in chunks:
        clean_chunk = re.sub('\s+', ' ', chunk)
        clean_chunk = clean_chunk.encode(encoding='ASCII',errors='ignore').decode()
        new_file.write(clean_chunk + "\n------------------\n")
   
chunks = db.get_document_chunks_from_doc_id(doc_id)
with open("prev.txt", 'w') as new_file:
    for chunk in chunks:
        chunk_text = chunk["chunk_text"]
        clean_chunk = re.sub('\s+', ' ', chunk_text)
        clean_chunk = clean_chunk.encode(encoding='ASCII',errors='ignore').decode()
        new_file.write(clean_chunk + "\n------------------\n")
   




