from flask import Flask
from app.views import main
from flask_pymongo import PyMongo
from config import Config
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    mongo = PyMongo(app)
    app.register_blueprint(main)

    # Configure the app using environment variables
    app.config['SERVERS_INFO_JSON'] = os.getenv('SERVERS_INFO_JSON')
    app.config['SERVER_INFO_T3_WHEAT'] = os.getenv('SERVER_INFO_T3_WHEAT')
    app.config['SERVER_INFO_T3_BARLEY'] = os.getenv('SERVER_INFO_T3_BARLEY')
    app.config['SERVER_INFO_T3_OAT'] = os.getenv('SERVER_INFO_T3_OAT')


    return app
