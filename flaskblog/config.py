import os


class Config:
    # need SECRET_KEY to prevent CSRF, on deployment should be in an environment variable I believe
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # set database url, sqlite for dev will switch to postgres for launch
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('APP_TEST_EMAIL')
    MAIL_PASSWORD = os.environ.get('APP_TEST_EMAIL_PASS')
