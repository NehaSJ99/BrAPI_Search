from flask import Flask
from app.views import main
from flask_pymongo import PyMongo
from config import Config

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    mongo = PyMongo(app)
    app.register_blueprint(main)
    return app
