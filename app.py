from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_mongoengine import MongoEngine
from datetime import datetime
from mongoengine import StringField, ReferenceField, ListField, EmailField, ImageField, DateTimeField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd5a2a902fe9f3fbadf29732b69ede5c8'
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb+srv://xedriq:xedriq@cluster0-811so.mongodb.net/flask_mongo_db?retryWrites=true&w=majority'
}
db = MongoEngine(app)


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


posts = [
    {
        'author': 'Cedrick Tabares',
        'title': 'Blog Post 1',
        'content': 'Blog 1 content',
        'date_posted': 'December 2, 2020'
    },
    {
        'author': 'John Tabares',
        'title': 'Blog Post 2',
        'content': 'Blog 2 content',
        'date_posted': 'January 2, 2020'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts, title='Home')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'cedrick@email.com' and form.password.data == 'pass':
            flash(f'Welcome to your dashboard!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Unable to login, please check email and password.', 'danger')
    return render_template('login.html', title="Login", form=form)


if __name__ == '__main__':
    app.run(debug=True)
