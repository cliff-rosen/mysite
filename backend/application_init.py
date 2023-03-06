from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from logger import Logger

def create_application():
    application = Flask(__name__)
    CORS(application)

    logger = Logger('api.log')
    application.logger = logger
    application.logger.debug('Initializing application...')

    return application

application = create_application()

def get_application():
    return application