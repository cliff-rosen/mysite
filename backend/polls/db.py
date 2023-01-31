import mariadb
import json

def getConnection():
    conn = mariadb.connect(
        user="nodejs",
        password="db",
        host="localhost",
        database="doc")
    return conn

def closeConnection(conn):
    conn.close()

def getAllDocuments(conn):
    cur = conn.cursor() 
    cur.execute("SELECT * FROM document") 
    return cur

def insertDocument(conn, source_id, title, text):
    cur = conn.cursor() 
    cur.execute("INSERT INTO document (doc_source_id, doc_title, doc_text) VALUES (?, ?, ?)", (source_id, title, text)) 
    conn.commit() 

def getAllDocumentChunks(conn):
    cur = conn.cursor() 
    cur.execute("SELECT * FROM document_chunk") 
    return cur

def insertDocumentChunk(conn, doc_id, chunk_text, chunk_embedding):
    json_data = json.dumps(chunk_embedding)
    cur = conn.cursor() 
    cur.execute("INSERT INTO document_chunk (doc_id, chunk_text, chunk_embedding) VALUES (?, ?, ?)", (doc_id, chunk_text, json_data)) 
    conn.commit() 

def updateDocumentChunkEmbedding(conn, doc_chunk_id, embedding):
    json_data = json.dumps(embedding)
    cur = conn.cursor()
    #cur.execute("UPDATE document_chunk SET chunk_text = '%s' WHERE id = (%s)", (json_data, doc_chunk_id)) 
    #cur.execute("SELECT * FROM document_chunk WHERE doc_chunk_id = ?", (doc_chunk_id,)) 
    cur.execute("UPDATE document_chunk SET chunk_embedding = ? WHERE doc_chunk_id = ?", (json_data, doc_chunk_id,)) 
    conn.commit() 

def getDocumentsFromIds(conn, ids):
    format_strings = ','.join(['%s'] * len(ids))
    cur = conn.cursor() 
    cur.execute("SELECT doc_id, doc_title FROM document WHERE doc_id in (%s)" % format_strings, tuple(ids)) 
    return cur

def getDocumentChunksFromIds(conn, ids):
    format_strings = ','.join(['%s'] * len(ids))
    cur = conn.cursor() 
    cur.execute("SELECT doc_chunk_id, chunk_text FROM document_chunk WHERE doc_chunk_id in (%s)" % format_strings, tuple(ids)) 
    return cur

def testInsert():
    conn = getConnection()
    insertDocument(conn, "id xyz", "another document", "more document text")

def testGet():
    conn = getConnection()
    cur = getDocumentsFromIds(conn, [7,8])
    for doc_id, doc_title in cur: 
        print(f"id: {doc_id}, title: {doc_title}")
    closeConnection(conn)

#testGet()
