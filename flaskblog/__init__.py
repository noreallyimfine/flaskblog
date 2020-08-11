import os
from flask import Flask
# import for using sql db through flask
from flask_sqlalchemy import SQLAlchemy
# import for encrypting passwords
from flask_bcrypt import Bcrypt
# import for handling logged in sessions
from flask_login import LoginManager
from flask_mail import Mail

# instantiate app
app = Flask(__name__)
# need SECRET_KEY to prevent CSRF, on deployment should be in an environment variable I believe
app.config['SECRET_KEY'] = '822c98eca6467896aa98a99444439fcf'
# set database url, sqlite for dev will switch to postgres for launch
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# create objects of each connected to app
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# set some login attributes
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('APP_TEST_EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('APP_TEST_EMAIL_PASS')
mail = Mail(app)
# import down here bec routes imports from this file.
# (The linter doesnt like this, wonder if there is another way to handle)
from flaskblog.users.routes import users
from flaskblog.posts.routes import posts
from flaskblog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
