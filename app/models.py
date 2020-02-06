from datetime import datetime
from mongoengine import StringField, ReferenceField, ListField, EmailField, ImageField, DateTimeField
from app import db


class User(db.Document):
    username = StringField(
        required=True, unique=True, min_length=2, max_length=20)
    email = EmailField(required=True, unique=True)
    image_file = ImageField(required=True, default='default.jpg')
    password = StringField(required=True)
    posts = ListField(ReferenceField('Post'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Document):
    title = StringField(max_length=100)
    date_posted = DateTimeField(required=True, default=datetime.utcnow)
    content = StringField(required=True)
    author = ReferenceField(User)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"
