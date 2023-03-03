import secrets
import string
import jwt
import datetime
import bcrypt
import local_secrets
import openai
OPENAI_API_KEY = local_secrets.OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

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

#print(encrypt_password('xogene5!'))
#model = 'gpt-3.5-turbo'
model = 'text-davinci-003'
prompt = 'hello'
temperature = .4

def answer_1():
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=500,
        temperature=temperature,
        stop="Patient:"
    )

    print(response["choices"][0]["text"].strip(" \n"))

def answer_2():
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
    )

    print(completion.choices[0].message)    

#answer_1()
#answer_2()

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
]

print(str(messages))