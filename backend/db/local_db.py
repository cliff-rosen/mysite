import mariadb
import json

"""
domain: domain_id, domain_desc
document: doc_id, domain_id, doc_uri, doc_text
document_chunk: doc_chunk_id, doc_id, chunk_text, chunk_embedding
index: doc_chunk_id, embedding, metadata {sub_index: <SUB_INDEX>}
"""

def get_connection():
    conn = mariadb.connect(
        user="nodejs",
        password="db",
        host="localhost",
        database="doc")
    return conn

def close_connection(conn):
    conn.close()

def insert_document(conn, domain_id, doc_uri, doc_title, doc_text):
    cur = conn.cursor() 
    cur.execute("INSERT INTO document (domain_id, doc_uri, doc_title, doc_text) VALUES (?, ?, ?, ?)", (domain_id, doc_uri, doc_title, doc_text)) 
    conn.commit() 

def get_all_docs_from_domain(conn, domain_id):
    cur = conn.cursor() 
    cur.execute("SELECT doc_id, domain_id, doc_uri, doc_title, doc_text FROM document WHERE domain_id = ? and doc_id > 3269", (domain_id,)) 
    return cur

def insert_document_chunk(conn, doc_id, chunk_text, chunk_embedding):
    json_data = json.dumps(chunk_embedding)
    cur = conn.cursor() 
    cur.execute("INSERT INTO document_chunk (doc_id, chunk_text, chunk_embedding) VALUES (?, ?, ?)", (doc_id, chunk_text, json_data)) 
    conn.commit() 

def get_document_chunks(conn, domain_id):
    cur = conn.cursor() 
    cur.execute("""
        SELECT d.doc_id, dc.doc_chunk_id, dc.chunk_embedding
        FROM document_chunk dc
        JOIN document d ON dc.doc_id = d.doc_id
        WHERE d.domain_id = ?
        """, (domain_id,)) 
    return cur

def get_document_chunks_from_ids(conn, ids):
    format_strings = ','.join(['%s'] * len(ids))
    cur = conn.cursor() 
    cur.execute("SELECT doc_chunk_id, chunk_text FROM document_chunk WHERE doc_chunk_id in (%s)" % format_strings, tuple(ids)) 
    return cur

def get_domains(conn):
    cur = conn.cursor() 
    cur.execute("SELECT domain_id, domain_desc FROM domain") 
    return cur

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


def testInsert():
    conn = getConnection()
    insertDocument(conn, "id xyz", "another document", "more document text")

def test_get():
    conn = get_connection()
    cur = get_domains(conn)
    for domain_id, domain_desc in cur: 
        print(f"id: {domain_id}, desc: {domain_desc}")
    close_connection(conn)

#test_get()
