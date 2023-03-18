import pinecone
import openai
from openai.embeddings_utils import get_embedding
from db import local_db as db
from utils.utils import num_tokens_from_string
import local_secrets as secrets

PINECONE_API_KEY = secrets.PINECONE_API_KEY
OPENAI_API_KEY = secrets.OPENAI_API_KEY
EMBEDDING_MODEL = "text-embedding-ada-002"
COMPLETION_MODEL = 'text-davinci-003'
INDEX_NAME = "main-index-2"
TEMPERATURE = .4
TOP_K = 20

pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)
openai.api_key = OPENAI_API_KEY

def ge(text):
    return get_embedding(
        text,
        engine=EMBEDDING_MODEL
    )

print('starting')

e_prev = None

for n in range(10):
    print('getting embedding', n)
    e = ge('What is the intervention trial number?')
    if e_prev:
        if (x == y for x, y in zip(e, e_prev)):
            print(n, "good")
        else:
            print(n, "bad")
            print(e_prev, e)
            break
    e_prev = e
print('done')