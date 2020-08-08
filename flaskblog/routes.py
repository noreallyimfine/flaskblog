# secrets module to hash filenames of profile pics
import secrets
# os to manipulate filename of profile pic
import os
# Image to resize images
from PIL import Image
# render_template makes use of flask templates - pass FILENAME of template, as well as any variables needed inside
# url_for gets the function name passed to it, and is best practice when linking around
# flash flashes messages
# redirect combines with url_for when we want a func to redirect to another page
# request handles POST data -> in this case when you try to access a page but get redirected to login, it remembers where you were trying to go
# abort is to stop their action and return an error
from flask import render_template, url_for, flash, redirect, request, abort
# these are all created in the __init__ file, related to our instance of the app
from flaskblog import app, db, bcrypt
# Database models
from flaskblog.models import User, Post
# Forms for inputs
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
# flask module handling user sessions
from flask_login import login_user, current_user, logout_user, login_required

# home route, also root
@app.route("/")
@app.route("/home")
# function called home
def home():
    # query db for all posts
    posts = Post.query.all()
    # render template for home.html, passing posts variable to display on home page
    return render_template("home.html", posts=posts)


# about route
@app.route("/about")
def about():
    return render_template("about.html")


# register route, also accepts POST
@app.route("/register", methods=['GET', 'POST'])
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
@app.route("/login", methods=["GET", 'POST'])
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


# func to rename, resize and save picture both to user model and static/profile_pics dir
def save_picture(form_picture):
    # get random hash for filename
    random_hex = secrets.token_hex(8)
    # we just care about the extension part (jpg or png)
    _, f_ext = os.path.splitext(form_picture.filename)
    # rejoin to a filename again
    picture_fn = random_hex + f_ext
    # create full path
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # use Image class to resize image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    # return new filename
    return picture_fn


# account route, also accepts POST
@app.route("/account", methods=['GET', 'POST'])
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


# logout route
@app.route("/logout")
def logout():
    # session handler to logout
    logout_user()
    # send them home
    return redirect(url_for('home'))


# new post route, also accepts POST
@app.route("/post/new", methods=['GET', 'POST'])
# required login decorator
@login_required
def new_post():
    # create that form
    form = PostForm()
    # did they submit a valid form?
    if form.validate_on_submit():
        # create a Post
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        # add to db
        db.session.add(post)
        db.session.commit()
        # show message
        flash('Your post has been created!', 'success')
        # send them home after logging in
        return redirect(url_for('home'))
    # for GET request, just base create post template
    return render_template('create_post.html', title='New Post',
                           form=form, legend="New Post")


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated", 'succes')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend="Update Post")


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
