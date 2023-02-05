#import mariadb
import pymysql.cursors
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import local_secrets as secrets

DB_SECRETS = secrets.DB_SECRETS

"""
domain: domain_id, domain_desc
document: doc_id, domain_id, doc_uri, doc_text
document_chunk: doc_chunk_id, doc_id, chunk_text, chunk_embedding
index: doc_chunk_id, embedding, metadata {sub_index: <SUB_INDEX>}
"""

def get_connection():
    conn = pymysql.connect(
        user=DB_SECRETS["DB_USER"],
        password=DB_SECRETS["DB_PASSWORD"],
        host=DB_SECRETS["DB_HOST"],
        database=DB_SECRETS["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor)
    return conn

def close_connection(conn):
    conn.close()

######################################
def validate_user(conn):
    query_string = """
                    SELECT user_id, user_name, password
                    FROM user
                    WHERE UserName = ${userName}
                """

######################################
def insert_document(conn, domain_id, doc_uri, doc_title, doc_text):
    cur = conn.cursor() 
    cur.execute("INSERT INTO document (domain_id, doc_uri, doc_title, doc_text) VALUES (%s, %s, %s, %s)", (domain_id, doc_uri, doc_title, doc_text)) 
    conn.commit() 

def get_all_docs_from_domain(conn, domain_id):
    cur = conn.cursor() 
    cur.execute("SELECT doc_id, domain_id, doc_uri, doc_title, doc_text FROM document WHERE domain_id = %s", (domain_id,)) 
    rows = cur.fetchall()
    res = [(row['doc_id'], row['domain_id'], row['doc_uri'], row['doc_title'], row['doc_text']) for row in rows]
    return res

def insert_document_chunk(conn, doc_id, chunk_text, chunk_embedding):
    json_data = json.dumps(chunk_embedding)
    cur = conn.cursor() 
    cur.execute("INSERT INTO document_chunk (doc_id, chunk_text, chunk_embedding) VALUES (%s, %s, %s)", (doc_id, chunk_text, json_data)) 
    conn.commit() 

def get_document_chunks(conn, domain_id):
    print("Retrieving chunks for domain", domain_id)
    cur = conn.cursor() 
    cur.execute("""
        SELECT d.doc_id, dc.doc_chunk_id, dc.chunk_embedding
        FROM document_chunk dc
        JOIN document d ON dc.doc_id = d.doc_id
        WHERE d.domain_id = %s
        """, 
        (domain_id,)) 
    rows = cur.fetchall()
    print("Preparing results for rowcount = ", len(rows))
    res = [(row['doc_id'], row['doc_chunk_id'], row['chunk_embedding']) for row in rows]
    return res

def insert_query_log(domain_id, query_text, query_prompt, query_temp, response_text, response_chunk_ids, user_id):
    conn = get_connection()
    cur = conn.cursor() 
    cur.execute("""
        INSERT 
        INTO query_log (
            domain_id, query_text, query_prompt, query_temp, response_text, response_chunk_ids, user_id
            ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (domain_id, query_text, query_prompt, query_temp, response_text, response_chunk_ids, user_id)) 
    conn.commit() 
    close_connection(conn)

def get_document_chunks_from_ids(ids):
    format_strings = ','.join(['%s'] * len(ids))
    conn = get_connection()
    cur = conn.cursor() 
    cur.execute("SELECT doc_chunk_id, chunk_text FROM document_chunk WHERE doc_chunk_id in (%s)" % format_strings, tuple(ids)) 
    rows = cur.fetchall()
    close_connection(conn)
    res = [(row['doc_chunk_id'], row['chunk_text']) for row in rows]
    return res

def get_domains(conn):
    cur = conn.cursor() 
    cur.execute("SELECT domain_id, domain_desc FROM domain")
    rows = cur.fetchall()
    res = [(row['domain_id'], row['domain_desc']) for row in rows]
    return res

##############################################

def test_get_domains():
    conn = get_connection()
    res = get_domains(conn)
    for domain_id, domain_desc in res:
        print(domain_id, domain_desc)
    close_connection(conn)

def test_get_all_docs_from_domain():
    conn = get_connection()
    res = get_all_docs_from_domain(conn, 1)
    for doc_id, domain_id, doc_uri, doc_title, doc_text in res:
        print(doc_id, doc_uri)
    close_connection(conn)

def test_get_chunks_from_ids():
    conn = get_connection()
    res = get_document_chunks_from_ids(conn, ['36', '34', '30', '33', '32', '31', '35', '89', '66', '65'] )
    for doc_chunk_id, chunk_text in res:
        print(f"id: {doc_chunk_id}, title: {chunk_text[:20]}")
        words_in_chunk = len(chunk_text.split())
        print("words", words_in_chunk)
        print(doc_chunk_id)
    close_connection(conn)

#test_get_domains()
#test_get_chunks_from_ids()
#test_get_all_docs_from_domain()

##############################################

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
