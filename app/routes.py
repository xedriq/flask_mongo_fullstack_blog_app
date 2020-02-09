import os
import secrets

from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from app import app, bcrypt, db, mail
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    # items_per_page = 1
    # page_nb = page
    # offset = (page_nb - 1) * items_per_page
    # posts = Post.objects.skip(offset).limit(items_per_page)
    # posts = Post.objects()
    posts = Post.objects.paginate(page=page, per_page=5)
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

    output_size = (125, 125)
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
        'static', filename='images/profile_pictures/' + current_user.image_file, _external=True)

    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        Post(title=form.title.data, content=form.content.data,
             author=current_user.id).save()
        flash(f'Post has been created.', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='Create New Post', form=form)


@app.route('/post/<string:id>', methods=['GET'])
def post(id):
    try:
        post = Post.objects(id=id).get()
        return render_template('post.html', title=post.title, post=post)
    except:
        abort(404)


@app.route('/post/<string:id>/update', methods=['GET', 'POST'])
@login_required
def update_post(id):
    form = PostForm()

    try:
        post = Post.objects(id=id).get()
    except:
        abort(404)

    if post.author.id != current_user.id:
        abort(403)

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.save()
        flash(f'Post has been updated.', 'success')
        return redirect(url_for('post', id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update Post', form=form, is_updating=True)


@app.route('/post/<string:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    try:
        post = Post.objects(id=id).get()
        post.delete()
        flash(f'Post has been deleted.', 'success')
        return redirect(url_for('home'))
    except:
        abort(404)

    if post.author.id != current_user.id:
        abort(403)


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.objects(username=username).first_or_404()
    posts = Post.objects(author=user.id).paginate(page=page, per_page=5)
    posts_count = Post.objects(author=user.id).count()
    return render_template('user_post.html', posts=posts, title='Home', user=user, posts_count=posts_count)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@email.com', recipients=[user[0].email])
    msg.body = f'''To reset your password, please visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this email.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.objects(email=form.email.data)
        if not user:
            abort(404)
            
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)

    if not user:
        flash('That is invalid/expired token.', 'warning')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        user.save()
        flash(f'Your password has been updated. You can now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
