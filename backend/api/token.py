from db import local_db as db
import local_secrets as secrets
from logger import Logger

def get_token(username, password):
    res = db.get_user(username)
    print(res)
    if 'error' in res:
        res['status'] = "ERROR"
        if res['error'] == "USER_NOT_FOUND":
            res['error'] = "UNAUTHORIZED"
        return res
    return({"status":"SUCCESS"})

"""
    if 'error' in res:
        res['status'] = "ERROR"
        if res['error'] == "USER_NOT_FOUND" or res['error'] == "INVALID_PASSWORD":
            res['error'] = "UNAUTHORIZED"
        return res
"""