from flask import render_template, url_for, flash, redirect
from app.forms import RegistrationForm, LoginForm
from app import app

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
