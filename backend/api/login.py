from db import local_db as db

def login(username, password):
    res = db.validate_user(username, password)
    if 'error' in res:
        res['status'] = "ERROR"
        if res['error'] == "USER_NOT_FOUND" or res['error'] == "INVALID_PASSWORD":
            res['error'] = "UNAUTHORIZED"
        return res
    else:
        res['status'] = "SUCCESS"
        return res
    
