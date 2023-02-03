import os
print(os.getcwd())
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
import local_db as db

def get_domains():
    res = []
    conn = db.get_connection()
    cur = db.get_domains(conn)
    for domain_id, domain_desc in cur: 
        res.append({"domain_id": domain_id, "domain_desc": domain_desc})
    db.close_connection(conn)
    return res
    
