from db import local_db as db
import local_secrets as secrets
from logger import Logger
import jwt
import datetime

def make_jwt(user_id, username):
    payload = {
    'user_id': user_id,
    'username': username,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload, secrets.JWT_SECRET, algorithm='HS256')
    return token

def get_token(username, password):
    res = db.get_user(username)
    print(res)
    if 'error' in res:
        res['status'] = "ERROR"
        if res['error'] == "USER_NOT_FOUND":
            res['error'] = "UNAUTHORIZED"
        return res
    jwt = make_jwt(res["user_id"], res["user_name"])
    return({"status":"SUCCESS", "token": jwt})

"""
    if 'error' in res:
        res['status'] = "ERROR"
        if res['error'] == "USER_NOT_FOUND" or res['error'] == "INVALID_PASSWORD":
            res['error'] = "UNAUTHORIZED"
        return res
"""