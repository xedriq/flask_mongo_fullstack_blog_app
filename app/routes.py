import os
import secrets

from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from app import app, bcrypt
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


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
    users = User.objects()
    return render_template('home.html', posts=posts, title='Home')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')

        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        try:
            new_user.save()
            flash(f'Account created. You can now log in!', 'success')
            return redirect(url_for('login'))
        except:
            flash(f'username and/or email is taken.', 'warning')

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Login successfull', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Unable to login, please check email and password.', 'danger')
    return render_template('login.html', title="Login", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fname = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/images/profile_pictures', picture_fname)

    output_size = (125,125)        
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fname

@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        
        try:
            current_user.save()
            flash(f'Account update.', 'success')
            return redirect(url_for('account'))
        except:
            flash(f'username and/or email is taken.', 'danger')

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename='images/profile_pictures/' + current_user.image_file)

    return render_template('account.html', title='Account', image_file=image_file, form=form)
