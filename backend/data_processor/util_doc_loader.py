from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
import os
import sys
sys.path.append('db')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import local_db as db
import local_secrets as secrets


def read_text_from_file(file_path):
    with open(file_path, 'r') as new_file:
        #clean_chunk = re.sub('\s+', ' ', chunk_text)
        #clean_chunk = clean_chunk.encode(encoding='ASCII',errors='ignore').decode()
        return new_file.read()

fp = 'c:/Data/doc_import_3.txt'
text = read_text_from_file(fp)
text = text.encode(encoding='ASCII',errors='ignore').decode()

chunks = text.split('---')

for chunk in chunks:
    chunk = chunk.strip()
    print(chunk[:50])
    db.insert_doc_temp(chunk)
    print('----------------------------')
