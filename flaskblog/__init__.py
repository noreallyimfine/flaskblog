from flask import Flask
# import for using sql db through flask
from flask_sqlalchemy import SQLAlchemy
# import for encrypting passwords
from flask_bcrypt import Bcrypt
# import for handling logged in sessions
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config

# create objects of each connected to app
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
# set some login attributes
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    # instantiate app
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # import down here bec routes imports from this file.
    # (The linter doesnt like this, wonder if there is another way to handle)
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app
