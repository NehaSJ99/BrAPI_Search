import os

class Config:
    MONGO_URI = os.getenv('MONGO_URI', "mongodb://127.0.0.1:27017")