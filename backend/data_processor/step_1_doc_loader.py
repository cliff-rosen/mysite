from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
import os
import sys
sys.path.append('.\..')
from db import local_db as db
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger()
doc_parts = []

def write_to_file(text):
    directory = 'outputs'
    dest = 'pages.txt'
    with open(os.path.join(directory, dest), 'a') as new_file:
        new_file.write(text)

def read_text_from_file(file_path):
    with open(file_path, 'r') as new_file:
        #clean_chunk = re.sub('\s+', ' ', chunk_text)
        #clean_chunk = clean_chunk.encode(encoding='ASCII',errors='ignore').decode()
        return new_file.read()

def read_text_from_pdf(filepath):
    print(filepath)
    page_text = ''

    try:
        reader = PdfReader(filepath)
    except Exception as e:
        print("error reading document", e)
        return

    doc_parts = []
    for page in reader.pages:
        text = page.extract_text()
        text = text.encode(encoding='ASCII',errors='ignore').decode()
        doc_parts.append(text)
    page_text = "".join(doc_parts)
    return page_text

def write_text_to_db(uri, text):
    print("-> saving: ", uri)
    if not db.insert_document(conn, domain_id, uri, "", text):
        logger.info("DB ERROR: " + uri)
    return    

filedir = 'inputs/'
domain_id = 33

print('Starting job')

files = os.listdir(filedir)
conn = db.get_connection()
for file in files:
    print(file)
    print('------------')
    doc_text = read_text_from_pdf(filedir + file)
    write_text_to_db(file, doc_text)
db.close_connection(conn)

print('Complete')