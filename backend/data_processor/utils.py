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

OPENAI_API_KEY = secrets.OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY
MODEL = "text-similarity-babbage-001"
INDEX_NAME = "whc-site"
index = None

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

def compareTexts(t1, t2):
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

print("starting...")
#init()

q1 = "what is linux and windows"
q2 = "what is the difference between apples and oranges"
t = "linux is an operating system that is opensource.  windows is an operating system sold by microsoft."
#compare_queries(q1, q2, t)


q = "pollution"

t1 ="""
Benefits

Pollution Control
PURETi treated roads and buildings eat smog and reverse pollution by reducing criteria pollutants like NOx and PM 2.5. As powerful as planting trees.

Self-Cleaning
Windows, roofs and facades stay twice as clean for twice as long with grime preventing PURETi. Building appearance is preserved and maintenance reduced.

Odor Elimination
Scrubs air free of smoke, pet, food or human odors. PURETi doesnt mask odors. It breaks them down. Works great inside hotels, cars, homes or schools.

IAQ Improvement
PURETi treated windows, window coverings and light fixtures act as air scrubbers to reduce VOCs in interior spaces by 50% or more.

Sustainability
Saves energy with cooler roofs and cleaner PV panels. Saves water and chemicals with reduced washing. Enhances brand and building value. Helps earn LEED points.

Cost Savings
PURETi pays for itself by reducing maintenance costs.  Hard ROI savings in labor, energy, water and chemical use
"""

t2 = """
pollution
"""

compare_chunks(q, t1, t2)

