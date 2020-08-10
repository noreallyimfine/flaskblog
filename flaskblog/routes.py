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
from flaskblog import app, db, bcrypt, mail
# Database models
from flaskblog.models import User, Post
# Forms for inputs
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
# flask module handling user sessions
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



