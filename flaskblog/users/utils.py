# func to rename, resize and save picture both to user model and static/profile_pics dir
import secrets
import os
from PIL import Image
from flask import url_for
from flaskblog import app, mail
from flask_mail import Message


def save_picture(form_picture):
    # get random hash for filename
    random_hex = secrets.token_hex(8)
    # we just care about the extension part (jpg or png)
    _, f_ext = os.path.splitext(form_picture.filename)
    # rejoin to a filename again
    picture_fn = random_hex + f_ext
    # create full path
    picture_path = os.path.join(app.root_path,
                                'static/profile_pics',
                                picture_fn)

    # use Image class to resize image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    # return new filename
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, ignore this email.
"""
    mail.send(msg)
