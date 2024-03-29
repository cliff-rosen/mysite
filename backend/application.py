from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from flask_cors import CORS
from api import login, domain, prompt, answer, conversation, token
from api.errors import InputError
from utils.utils import decode_token
import logging

MAX_TOKENS_DEFAULT = 200
TEMPERATURE_DEFAULT = .4

LOG_LEVEL = logging.INFO
logging.basicConfig(format='%(asctime)s  %(levelname)s - %(message)s', level=LOG_LEVEL, filename='app2.log', filemode='w')
logger = logging.getLogger()

application = Flask(__name__)
CORS(application)

logger.info('Initializing application...')

parser = reqparse.RequestParser()
parser.add_argument('domain_id', type=int)

def authenticate():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
            decoded_token = decode_token(auth_token)
            #print(decoded_token)
            if 'error' in decoded_token:
                return False
        except IndexError:
            return False
    else:
        return False
    return True

"""
@app.route('/hello', methods=['POST'])
def hello():
    print(request.json)
    return 'Hello!'
"""
class Conversation(Resource):
    def post(self):
        logger.debug('Conversation called')

        if not authenticate():
            logger.warning('Conversation - Authentication failure')
            abort(401)
            #return {"status": "INVALID_TOKEN"}

        try:
            data = None
            data = request.get_json()
            prompt_header = data['promptHeader']
            initial_message = data['initialMessage']
            user_role_name = data['userRoleName']
            bot_role_name = data['botRoleName']
            conversation_history = data['conversationHistory']
            user_message = data['userMessage']
            max_tokens = data.get('max_tokens', MAX_TOKENS_DEFAULT)
            temperature = data.get('temperature', TEMPERATURE_DEFAULT)
            domain_id = data.get('domain_id', 0)
            model_id = data.get('model_id', 1)
        except Exception as e:
            data_str = str(data) if data else 'NO_DATA_PARSED'
            logger.warning('Conversation - Error parsing body: ' + data_str)
            abort(400)

        try:
            res = conversation.get_response(
                domain_id,
                prompt_header,
                initial_message,
                user_role_name,
                bot_role_name,
                conversation_history,
                user_message,
                max_tokens,
                temperature,
                model_id
            )
        except InputError as e:
            logger.warning('InputError in Conversation: %s', e)
            abort(400, message=str(e))
        except Exception as e:
            logger.error('Uncaught exception in Conversation.post: %s', e)
            abort(500)

        return res

class Token(Resource):
    def post(self):
        data = request.get_json()
        username=data["username"]
        password=data["password"]
        print("token", username, password)
        res = token.get_token(username, password)
        if res['status'] != "SUCCESS":
            if res['status'] == 'INVALID_LOGIN':
                return(res, 401)
            else:
                res['status'] = 'SERVER_ERROR'
                return(res, 500)
        return res

class Login(Resource):
    def get(self):
        username = request.args.get('username')
        password = request.args.get('password')
        res = login.login(username, password)
        if res['status'] == "ERROR":
            if res['error'] == 'UNAUTHORIZED':
                return(res, 401)
            else:
                return(res, 500)
        return res

class Domain(Resource):
    def get(self, domain_id=None):
        print("domain_id", domain_id)
        if domain_id is None:        
            res = domain.get_domains()
            return res
        else:
            res = domain.get_domain(domain_id)
            return res

class Prompt(Resource):
    def get(self):
        res = prompt.get_prompt()
        return res

class Answer(Resource):
    def post(self):
        # retrieve inputs
        data = request.get_json()
        #print("body", data)
        conversation_id=data["conversation_id"]
        domain_id = data["domain_id"]
        user_id = data["user_id"]
        query = data["query"]
        prompt_template = data["prompt_template"]
        temp = data["temp"]
        use_new_model = data["use_new_model"]
        print("domain_id", domain_id)
        print("query", query)
        print("temp", temp)

        # execute call to get_answer()
        res = answer.get_answer(conversation_id, domain_id, query, prompt_template, temp, user_id, use_new_model)
        return res

class Hello(Resource):
    def get(self):
        return "hello"

api = Api(application)
api.add_resource(Token, '/auth/token')
api.add_resource(Conversation, '/conversation')
api.add_resource(Login, '/login')
api.add_resource(Domain, '/domain', '/domain/<int:domain_id>')
api.add_resource(Prompt, '/prompt')
api.add_resource(Answer, '/answer')
api.add_resource(Hello, '/hello')

if __name__ == '__main__':
    application.run(debug=True)