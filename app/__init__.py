from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd5a2a902fe9f3fbadf29732b69ede5c8'
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb+srv://xedriq:xedriq@cluster0-811so.mongodb.net/flask_mongo_db?retryWrites=true&w=majority'
}
db = MongoEngine(app)

from app import routes