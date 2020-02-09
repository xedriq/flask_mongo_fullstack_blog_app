import os
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import  Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd5a2a902fe9f3fbadf29732b69ede5c8'
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb+srv://xedriq:xedriq@cluster0-811so.mongodb.net/flask_mongo_db?retryWrites=true&w=majority'
}
db = MongoEngine(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from app import routes