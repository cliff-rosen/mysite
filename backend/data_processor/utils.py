import pinecone
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
import re
import os
import sys
sys.path.append('db')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import local_db as db
import local_secrets as secrets
from logger import Logger
from tqdm import tqdm
import json

"""
PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY
MODEL = "text-similarity-babbage-001"
INDEX_NAME = "main-index"
"""

def ge(text):
    embedding_model = MODEL
    return get_embedding(
        text,
        engine=embedding_model
    )

def query(q):
    print("getting matches")
    matches = index.query(
        top_k=5,
        include_values=True,
        include_metadata=True,
        vector=q).matches
    print('length:', len(matches))
    for i in range(len(matches)):
        print(matches[i].metadata, matches[i].id, matches[i].score)

def compare_texts(t1, t2):
    e1 = ge(t1)
    e2 = ge(t2)
    sim = cosine_similarity(e1, e2)
    print(sim)
    return sim

def compare_queries(q1, q2, t):
    q1e = ge(q1)
    q2e = ge(q2)
    te = ge(t)
    print("q1 to t: ", cosine_similarity(q1e, te))
    print("q2 to t: ", cosine_similarity(q2e, te))

def compare_chunks(q, t1, t2):
    qe = ge(q)
    te1 = ge(t1)
    te2 = ge(t2)    
    print("q to t1: ", cosine_similarity(qe, te1))
    print("q to t2: ", cosine_similarity(qe, te2))

def delete_indexes(ids):
    print("deleting ids:", ids)
    res = index.delete(ids=ids)
    print("response", res)

def init():
    global index
    print("initing openai")
    openai.api_key = OPENAI_API_KEY
    print("initing pinecone")
    pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
    index = pinecone.Index(INDEX_NAME)
    #pl = pinecone.list_indexes()
    #print(pl)

#index = pinecone.Index("openai-trec")
#res = index.fetch(ids=['3890', '3891'])
#print(res['vectors']['3890']['metadata'])

"""
print("starting...")
index = None
init()
print(index.describe_index_stats())
ids = ('19826,19827,19828,19829,19830,19831,19832,19833,19834').split(",")
ids = ('19769,19780,19786,19821,19869').split(",")
print(ids)
delete_indexes(ids)
"""

q1 = "what is linux and windows"
q2 = "what is the difference between apples and oranges"
t = "linux is an operating system that is opensource.  windows is an operating system sold by microsoft."
#compare_queries(q1, q2, t)
#compare_chunks(q, t1, t2)

        
