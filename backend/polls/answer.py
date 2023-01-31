import pinecone
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
from . import db

PINECONE_API_KEY = "7484d7df-d798-4b27-90c7-0f0164e6744d"
OPENAI_API_KEY = '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'
MODEL = "text-embedding-ada-002"
INDEX_NAME = "whc-site"
TEMPERATURE=.5
TOP_K=4
pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")
index = pinecone.Index(INDEX_NAME)

def ge(text):
    embedding_model = MODEL
    return get_embedding(
        text,
        engine=embedding_model
    )

print("initing openai")
openai.api_key = OPENAI_API_KEY

def getDocidsFromIndex(query_embedding):
    print("getting matches")
    matches = index.query(
        top_k=TOP_K,
        include_values=True,
        include_metadata=True,
        vector=query_embedding).matches
    print('length:', len(matches))
    res = [int(matches[i].id) for i in range(len(matches))]
    return res

def getChunksFromIds(ids):
    conn = db.getConnection()
    cur = db.getDocumentChunksFromIds(conn, ids)
    res = []
    for doc_chunk_id, chunk_text in cur: 
        print(f"id: {doc_chunk_id}, title: {chunk_text[:20]}")
        res.append(chunk_text)
    db.closeConnection(conn)
    return res

def createPrompt(question, chunks):
    header = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, try to make a helpful suggestion if possible.  \n\nContext:\n"""
    prompt = header + "".join(chunks) + "\n\n Q: " + question + "\n A:"
    return prompt

def queryModel(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        temperature=TEMPERATURE
    )
    return response["choices"][0]["text"].strip(" \n")

def logResult(query, result):
    file_name = "log.txt"
    text = "QUERY: " + query + "\n\nRESPONSE: " + result + "\n\n========================================================\n\n"
    with open(file_name, "a") as file:
        file.writelines(text)

def writeChunksToSingleFile():
    file_name = "output.txt"
    text = ""
    conn = db.getConnection()
    cur = db.getAllDocumentChunks(conn)
    for doc_chunk_id, doc_id, chunk_text, chunk_embedding in cur: 
        print(f"id: {doc_chunk_id}, title: {chunk_text[:20]}")
        text = text + chunk_text + "\n\n"
    db.closeConnection(conn)
    text = text.encode(encoding='ASCII',errors='ignore').decode()
    with open(file_name, "a") as file:
        file.writelines(text)

def get_answer(query):

    print("getting query embedding")
    query_embedding = ge(query)

    print("getting chunks ids")
    ids = getDocidsFromIndex(query_embedding)
    print("chunk ids are: ", ids)

    print("getting chunks from ids")
    chunks = getChunksFromIds(ids)
    print("creating prompt")

    prompt = createPrompt(query, chunks)
    #print(prompt)

    print("querying model")
    response = queryModel(prompt)

    print("response", response)
    logResult(query, response)

    return {"answer" :response}

#writeChunksToSingleFile()
#print("get_answer()")