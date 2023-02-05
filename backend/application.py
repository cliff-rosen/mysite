from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
import answer
import domain
import login

application = Flask(__name__)
CORS(application)
api = Api(application)

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
    def get(self):
        res = domain.get_domains()
        return res

class Answer(Resource):
    def post(self):
        data = request.get_json()
        print("body", data)
        query = data["query"]
        domain_id = data["domain_id"]
        print("domain_id", domain_id)
        print("query", query)
        res = answer.get_answer(domain_id, query)
        return res

class Login(Resource):
    def get(self):
        username = request.args.get('username')
        password = request.args.get('password')
        res = login.login(username, password)
        return res

api.add_resource(Hello, '/hello')
api.add_resource(Domain, '/domain')
api.add_resource(Answer, '/answer')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    application.run(debug=True)