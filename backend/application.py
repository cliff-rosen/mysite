from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from api import login, domain, prompt, answer

application = Flask(__name__)
CORS(application)
api = Api(application)

parser = reqparse.RequestParser()
parser.add_argument('domain_id', type=int)

"""
@app.route('/hello', methods=['POST'])
def hello():
    print(request.json)
    return 'Hello!'
"""
class Hello(Resource):
    def get(self):
        return "hello"

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
        print("body", data)
        conversation_id=data["conversation_id"]
        domain_id = data["domain_id"]
        user_id = data["user_id"]
        query = data["query"]
        prompt_template = data["prompt_template"]
        temp = data["temp"]
        print("domain_id", domain_id)
        print("query", query)
        print("temp", temp)

        # execute call to get_answer()
        res = answer.get_answer(conversation_id, domain_id, query, prompt_template, temp, user_id, )
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

api.add_resource(Hello, '/hello')
api.add_resource(Login, '/login')
api.add_resource(Domain, '/domain', '/domain/<int:domain_id>')
api.add_resource(Prompt, '/prompt')
api.add_resource(Answer, '/answer')

if __name__ == '__main__':
    application.run(debug=True)