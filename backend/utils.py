import secrets
import string


def make_new_conversation_id():
    alphabet = string.ascii_letters + string.digits  
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return password

