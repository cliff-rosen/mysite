#import mariadb
import pymysql.cursors
import json
import os
import sys
import local_secrets as secrets

DB_SECRETS = secrets.DB_SECRETS

"""
domain: domain_id, domain_desc
document: doc_id, domain_id, doc_uri, doc_text
document_chunk: doc_chunk_id, doc_id, chunk_text, chunk_embedding
index: doc_chunk_id, embedding, metadata {sub_index: <SUB_INDEX>}
"""

##### CONNECTIONS #####

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

def l_to_d(keys, values):
    return dict(zip(keys, values))

##### USER #####

def validate_user(user_name, password):
    query_string = """
                    SELECT user_id, user_name, password,
                        user_description, domain_id
                    FROM user
                    WHERE user_name = %s
                """
    try:
        print("getting connection")
        conn = get_connection()
        cur = conn.cursor() 
        cur.execute(query_string, (user_name,)) 
        rows = cur.fetchall()
        close_connection(conn)
    except Exception as e:
        return {'error': 'DB_CONNECTION_ERROR'}

    if len(rows) == 0:
        return {"error": "USER_NOT_FOUND"}
    elif len(rows) > 1:
        return {"error": "DB_ERROR"}
    elif rows[0]["password"] != password:
        return {"error": "INVALID_PASSWORD"}
    user= rows[0]
    del user['password']
    return user


##### DOCUMENT PIPELINE #####

def insert_document(conn, domain_id, doc_uri, doc_title, doc_text):
    try:
        cur = conn.cursor() 
        cur.execute("INSERT INTO document (domain_id, doc_uri, doc_title, doc_text) VALUES (%s, %s, %s, %s)", (domain_id, doc_uri, doc_title, doc_text)) 
        conn.commit() 
    except Exception as e:
        print("***************************")
        print(doc_uri)
        print("DB error in insert_document:\n", str(e))
        return False
    return True

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

def update_document_chunk_embedding(conn, doc_chunk_id, embedding):
    json_data = json.dumps(embedding)
    cur = conn.cursor()
    cur.execute("UPDATE document_chunk SET chunk_embedding = %s WHERE doc_chunk_id = %s", (json_data, doc_chunk_id,)) 
    conn.commit() 

def get_document_chunks(conn, domain_id):
    print("Retrieving chunks for domain", domain_id)
    cur = conn.cursor() 
    cur.execute("""
        SELECT d.doc_id, dc.doc_chunk_id, dc.chunk_embedding, dc.chunk_text
        FROM document_chunk dc
        JOIN document d ON dc.doc_id = d.doc_id
        WHERE d.domain_id = %s
        """, 
        (domain_id,)) 
    rows = cur.fetchall()
    return rows

##### ANSWER #####

def get_document(doc_id):
    conn = get_connection()
    cur = conn.cursor() 
    cur.execute("SELECT * FROM document where doc_id = %s", (doc_id,))
    rows = cur.fetchall()
    close_connection(conn)    
    return rows

def get_document_chunks_from_ids(ids):
    ids_text = ",".join(ids)
    conn = get_connection()
    cur = conn.cursor() 
    query_text = """
        SELECT dc.doc_chunk_id, dc.chunk_text, d.doc_uri
        FROM document_chunk dc
        JOIN document d ON dc.doc_id = d.doc_id
        WHERE dc.doc_chunk_id in (%s)
        """ % (ids_text,)
    print(query_text)
    cur.execute(query_text) 
    rows = cur.fetchall()
    close_connection(conn)
    #res = [(row['doc_chunk_id'], row['chunk_text']) for row in rows]
    return rows

def get_document_chunks_from_doc_id(id):
    conn = get_connection()
    cur = conn.cursor() 
    query_text = """
        SELECT dc.doc_chunk_id, dc.chunk_text, d.doc_uri
        FROM document_chunk dc
        JOIN document d ON dc.doc_id = d.doc_id
        WHERE d.doc_id = %s
        order by dc.doc_chunk_id
        """ % (id,)
    cur.execute(query_text) 
    rows = cur.fetchall()
    close_connection(conn)
    return rows

##### DOMAIN #####

def get_domains():
    conn = get_connection()
    cur = conn.cursor() 
    cur.execute("SELECT domain_id, domain_desc FROM domain ORDER BY domain_desc")
    rows = cur.fetchall()
    close_connection(conn)    
    return rows

def get_domain(domain_id):
    conn = get_connection()
    cur = conn.cursor() 
    cur.execute("""
                SELECT  domain_id, domain_desc,
                        initial_prompt_template, followup_prompt_template,
                        initial_conversation_message
                FROM    domain
                WHERE   domain_id = %s
                """, (domain_id,))
    rows = cur.fetchall()
    close_connection(conn)    
    return rows[0]


##### CONVERSATION #####

def insert_conversation(
        conversation_id,
        user_id,
        domain_id,
        conversation_text
        ):
    try:
        conn = get_connection()
        cur = conn.cursor() 
        cur.execute("""
            INSERT 
            INTO conversation (
                conversation_id,
                user_id,
                domain_id,
                conversation_text
                ) 
            VALUES (%s, %s, %s, %s)
            """,
            (conversation_id, user_id, domain_id, conversation_text)) 
        conn.commit() 
    except Exception as e:
        print("***************************")
        print("DB error in insert_conversation")
        print(e)
    close_connection(conn)


def get_conversation(conversation_id):
    rows = None
    try:
        conn = get_connection()
        cur = conn.cursor() 
        cur.execute("""
            SELECT 
                conversation_id,
                user_id,
                domain_id,
                conversation_text
            FROM conversation
            WHERE conversation_id = %s
            """,
            (conversation_id, )) 
        rows = cur.fetchall()
    except Exception as e:
        print("***************************")
        print("DB error in get_conversation")
        print(e)
    close_connection(conn)    
    return rows

def get_conversation_history(conversation_id):
    rows = None
    try:
        conn = get_connection()
        cur = conn.cursor() 
        cur.execute("""
            SELECT 
                conversation_id, query_id,
                user_id, domain_id,
                query_text,
                response_text
            FROM query_log
            WHERE conversation_id = %s
            ORDER BY query_id
            """,
            (conversation_id, )) 
        rows = cur.fetchall()
    except Exception as e:
        print("***************************")
        print("DB error in get_conversation_history")
        print(e)
    close_connection(conn)    
    return rows


def update_conversation(conversation_id, conversation_text):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE  conversation
            SET     conversation_text = %s
            WHERE   conversation_id = %s
            """,
            (conversation_text, conversation_id, )) 
        conn.commit()         
    except Exception as e:
        print("***************************")
        print("DB error in update_conversation")
        print(e)
    close_connection(conn)    


##### MISC #####

def insert_query_log(domain_id, query_text, query_prompt, query_temp, response_text, response_chunk_ids, user_id, conversation_id = ""):
    try:
        conn = get_connection()
        cur = conn.cursor() 
        cur.execute("""
            INSERT 
            INTO query_log (
                domain_id, query_text, query_prompt, query_temp, response_text, response_chunk_ids, user_id, conversation_id
                ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (domain_id, query_text, query_prompt, query_temp, response_text, response_chunk_ids, user_id, conversation_id)) 
        conn.commit() 
    except Exception as e:
        print("***************************")
        print("DB error in insert_query_log")
        print(e)
    close_connection(conn)

def insert_doc_temp(doc_text):
    try:
        conn = get_connection()
        cur = conn.cursor() 
        cur.execute("""
            INSERT 
            INTO doc_temp (
                doc_text
            )
            VALUES (%s)
            """,
            (doc_text,)) 
        conn.commit() 
    except Exception as e:
        print("***************************")
        print("DB error in insert_doc_temp")
        print(e)
        return False
    close_connection(conn)
    return True


##### TESTS #####

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

def test_validate_user(user_name, password):
    res = validate_user(user_name, password)
    print(res)

#test_get_domains()
#test_get_chunks_from_ids()
#test_get_all_docs_from_domain()
#test_validate_user("cliff", "cmr")

##### ARCHIVE #####

def getDocumentsFromIds(conn, ids):
    format_strings = ','.join(['%s'] * len(ids))
    cur = conn.cursor() 
    cur.execute("SELECT doc_id, doc_title FROM document WHERE doc_id in (%s)" % format_strings, tuple(ids)) 
    return cur

