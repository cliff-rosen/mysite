import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
import local_db as db

def get_domains():
    rows = db.get_domains()
    return rows
    