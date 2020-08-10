from flask import Blueprint, redirect, url_for, render_template, flash, request
from flaskblog import bcrypt, db
from flaskblog.users.forms import (RegistrationForm, RequestResetForm,
                                   ResetPasswordForm, LoginForm,
                                   UpdateAccountForm)
from flask_login import current_user, login_user, logout_user, login_required
from flaskblog.models import User, Post
from flasklog.users.utils import send_reset_email, save_picture

users = Blueprint('users', __name__)


# register route, also accepts POST
@users.route("/register", methods=['GET', 'POST'])
def register():
    # is user logged in? <- this probably actually means if they're registration is successful?
    # how do they get to login if they are already logged in, maybe they typed in the URL
    if current_user.is_authenticated:
        # send them to the home page, they dont need to login
        return redirect(url_for('home'))
    # isntantiate the form
    form = RegistrationForm()
    # did they validly submit a form?
    if form.validate_on_submit():
        # lets hash that password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # get the username from the data
        username = form.username.data
        # create a User model instance
        user = User(username=username,
                    email=form.email.data,
                    password=hashed_password)
        # add user to db
        db.session.add(user)
        db.session.commit()
        # show message
        flash(f'Account created for {username}!, you can now log in!',
              'success')
        # using that redirect->url and it receives the function name for the login route
        return redirect(url_for('login'))
    # if its just GET request, show them the registration form
    return render_template('register.html', title='Register', form=form)


# login route, also accepts POST
@users.route("/login", methods=["GET", 'POST'])
def login():
    # if they are already loggged in
    if current_user.is_authenticated:
        # send them home, notice redirect and 'home' is function name
        return redirect(url_for('home'))
    # login form created
    form = LoginForm()
    # did they submit the form?
    if form.validate_on_submit():
        # search db for email they put in
        user = User.query.filter_by(email=form.email.data).first()
        # if user exists, and the password matches our saved one
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # user session management to log in user, check if they want to be rememebered
            login_user(user, remember=form.remember.data)
            # look for the page they were trying ot get to that redirected them here
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        # login fails
        else:
            # tell them and stay on the page
            flash('Login Unsuccessful. Please check username and password',
                  'danger')
    # GET request just returns the base page
    return render_template('login.html', title='Register', form=form)


# logout route
@users.route("/logout")
def logout():
    # session handler to logout
    logout_user()
    # send them home
    return redirect(url_for('home'))


# account route, also accepts POST
@users.route("/account", methods=['GET', 'POST'])
# login required decorator
@login_required
def account():
    # option to update account
    form = UpdateAccountForm()
    # did they submit and correctly?
    if form.validate_on_submit():
        # is there a picture
        if form.picture.data:
            # handle it.
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        # update username and email
        current_user.username = form.username.data
        current_user.email = form.email.data
        # commit to db
        db.session.commit()
        # show message
        flash('Your account has been updated!',
              'success')
        # send back to account page (to display the changes prolly we need to reload)
        return redirect(url_for('account'))
    # oh is it a get request?
    elif request.method == 'GET':
        # gotta show their current username and email
        form.username.data = current_user.username
        form.email.data = current_user.email
    # load their profile pic, url_for can be used not just getting routes?
    # url_for probbably just generates the url, the redirect sends us there.
    # interesting that we do a function something and now a filepath to a file
    image_file = url_for('static',
                         filename='profile_pics/' + current_user.image_file)
    # then render the account page with the image and the form
    return render_template('account.html',
                           title='Account',
                           image_file=image_file,
                           form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been changed! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)