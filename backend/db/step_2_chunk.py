import db
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
# embedding length: 1536

OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY

def ge(text):
    embedding_model = "text-embedding-ada-002"
    return get_embedding(
        text,
        engine="text-embedding-ada-002"
    )

def getAllDocuments():
    return db.getAllDocuments(conn)

# init
conn = db.getConnection()

# one to one creation of chunks with embeddings
# FIX ME: this should instead break docs into chunks
# FIX ME: should be upsertChunk() and not insertChunk()
rows = getAllDocuments().fetchall()
for row in rows:
    print(row[1])
    embedding = ge(row[3])
    db.insertDocumentChunk(conn, row[0], row[3], embedding)

# cleanup
db.closeConnection(conn)
