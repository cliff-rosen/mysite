from db import local_db as db
from utils import check_password, make_jwt, decode_token


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
    if check_password(password, hashed_password):
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