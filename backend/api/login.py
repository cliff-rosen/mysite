import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
import local_db as db

def login(username, password):
    return db.validate_user(username, password)
    