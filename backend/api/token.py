from db import local_db as db
import local_secrets as secrets
from logger import Logger
import jwt
import datetime
import bcrypt

def make_jwt(user_id, username):
    payload = {
    'user_id': user_id,
    'username': username,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload, secrets.JWT_SECRET, algorithm='HS256')
    return token

def get_token(username, password):
    # get user record
    res = db.get_user(username)
    print('get_user', res)
    if res['result'] != 'SUCCESS':
        if res['result'] == 'USER_NOT_FOUND':
            print('get_token error - user not found')
            return {'status': 'INVALID_LOGIN'}
        else:
            print('get_token error', res)
            return {'status', 'db error'}
    
    # verify and return
    hashed_password = res['hashed_password']
    #hashed_password = bcrypt.hashpw(res['password'].encode('utf-8'), bcrypt.gensalt())
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        jwt = make_jwt(res['user_id'], res['user_name'])
        return({"status":"SUCCESS", "token": jwt})
    else:
        print('get_token error - invalid password')
        return({"status": "INVALID_LOGIN"})

"""
    if 'error' in res:
        res['status'] = "ERROR"
        if res['error'] == "USER_NOT_FOUND" or res['error'] == "INVALID_PASSWORD":
            res['error'] = "UNAUTHORIZED"
        return res
"""