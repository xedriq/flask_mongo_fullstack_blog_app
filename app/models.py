from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mongoengine import StringField, ReferenceField, ListField, EmailField, ImageField, DateTimeField
from app import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


class UserCustomQuerySet(db.QuerySet):
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': str(self[0].id)}).decode('utf-8')

    


class User(db.Document, UserMixin):
    username = StringField(
        required=True, unique=True, min_length=2, max_length=20)
    email = EmailField(required=True, unique=True)
    image_file = StringField(required=True, default='default.jpg')
    password = StringField(required=True)
    posts = ListField(ReferenceField('Post'))

    meta = {'queryset_class': UserCustomQuerySet}

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
        except:
            return None

        return User.objects(id=user_id).get()

class Post(db.Document):
    title = StringField(max_length=100)
    date_posted = DateTimeField(required=True, default=datetime.utcnow)
    content = StringField(required=True)
    author = ReferenceField(User)

    def __repr__(self):
        return f"User('{self.title}', '{self.date_posted}')"

    meta = {
        'ordering': ["-date_posted"]
    }
