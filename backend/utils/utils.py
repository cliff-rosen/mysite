import secrets
import string
import jwt
import datetime
import bcrypt
import tiktoken
import local_secrets


def make_new_conversation_id():
    alphabet = string.ascii_letters + string.digits  
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return password

def encrypt_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password

def check_password(password, hashed_password):
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        return True
    return False

def make_jwt(user_id, username):
    payload = {
    'user_id': user_id,
    'username': username,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload, local_secrets.JWT_SECRET, algorithm='HS256')
    return token

def decode_token(jwt_token):
    try:
        decoded_token = jwt.decode(jwt_token, local_secrets.JWT_SECRET, algorithms=["HS256"])
    except Exception as e:
        print('decode_token_error', e)
        return {'error', str(e)}
    return(decoded_token)


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)

    num_tokens = len(encoding.encode(string))
    return num_tokens
