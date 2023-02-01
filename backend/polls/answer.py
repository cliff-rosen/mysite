import pinecone
import openai
from openai.embeddings_utils import get_embedding
from . import db
from . import secrets

PINECONE_API_KEY = "7484d7df-d798-4b27-90c7-0f0164e6744d"
OPENAI_API_KEY = secrets.OPENAI_API_KEY
MODEL = "text-embedding-ada-002"
INDEX_NAME = "whc-site"
TEMPERATURE=.5
TOP_K=10
MAX_WORD_COUNT = 2500

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

def get_chunks_from_embedding(query_embedding):
    print("getting matches")
    matches = index.query(
        top_k=TOP_K,
        include_values=True,
        include_metadata=True,
        vector=query_embedding).matches
    print('length:', len(matches))
    #matches = sorted(matches, key = lambda match: match.score, reverse = True)
    res = {matches[i].id : {"id" : int(matches[i].id), "score" : matches[i].score} for i in range(len(matches))}
    return res

def get_chunks_with_text(chunks):
    print("getting chunks with text")
    chunks_with_text = {}
    word_count = 0

    # add text property to chunks
    ids = list(chunks.keys())
    conn = db.getConnection()
    cur = db.getDocumentChunksFromIds(conn, ids)
    for doc_chunk_id, chunk_text in cur:
        print(f"id: {doc_chunk_id}, title: {chunk_text[:20]}")
        words_in_chunk = len(chunk_text.split())
        print("words", words_in_chunk)
        chunks[str(doc_chunk_id)]["text"] = chunk_text
    db.closeConnection(conn)

    # add chunks to chunks_with_text until word_count grows too large
    for id, chunk in sorted(chunks.items(), key=lambda item: item[1]["score"], reverse = True):
        words_in_chunk = len(chunk["text"].split())
        print("words", words_in_chunk)
        if word_count + words_in_chunk > MAX_WORD_COUNT:
            break
        chunks_with_text[str(chunk["id"])] = chunk
        chunks_with_text[str(chunk["id"])]["text"] = chunk["text"]
        word_count = word_count + words_in_chunk

    print('word count', word_count)
    return chunks_with_text


def create_prompt(question, chunks):
    ids = list(chunks.keys())
    chunks_text_arr = [chunks[str(id)]["text"] for id in ids]
    header = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, try to make a helpful suggestion if possible.  \n\nContext:\n"""
    prompt = header + "".join(chunks_text_arr) + "\n\n Q: " + question + "\n A:"
    return prompt

def query_model(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        temperature=TEMPERATURE
    )
    return response["choices"][0]["text"].strip(" \n")

def get_answer(query):

    print("getting query embedding")
    query_embedding = ge(query)

    print("getting chunks ids")
    chunks = get_chunks_from_embedding(query_embedding)

    print("getting chunk text from ids")
    chunks_with_text = get_chunks_with_text(chunks)

    print("creating prompt")
    prompt = create_prompt(query, chunks_with_text)
    #print(prompt)

    print("querying model")
    response = query_model(prompt)

    #print("response", response)
    #logResult(query, response)

    return {"answer": response, "chunks": chunks, "chunks_used_count": len(list(chunks_with_text.keys())) }


