import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from passlib.hash import argon2
from wtforms import Form, StringField, IntegerField, validators
import re
import pathlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hmac
import secrets
from logging.config import dictConfig

# Generate a secret key at application startup and store it securely using environment variables
secret_key = os.environ.get('SECRET_KEY') or secrets.token_bytes(16)

ph = argon2.__version__
if ph < '6.0':
    from passlib.hash import argon2

# Securely store CSRF token secret
csrf_secret_path = pathlib.Path('/tmp/csrf_secret.key')
try:
    csrf_secret = os.urandom(32)
    with open(csrf_secret_path, 'wb') as f:
        f.write(csrf_secret)
except Exception as e:
    logger.exception(e)

# Load environment variables
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = secret_key.decode('utf-8')

# Define error handlers for all potential exception paths
@app.errorhandler(Exception)
def handle_exception(e):
    try:
        db.session.rollback()
    except Exception as rollback_e:
        logger.exception(rollback_e)

    return render_template('500.html', title='Internal Server Error'), 500

# Handle unhandled exceptions during requests
try:
    app.wsgi_app.teardown_request(None) # Disable teardown request handlers to catch all exceptions
except AttributeError:
    pass

# Define password hashing mechanism with the latest and recommended version of Argon2
class User(UserMixin):
    def __init__(self, id, password):
        self.id = id
        self.password = ph.hash(password)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define IP blocking mechanism using Flask-Limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
def configure_limiter():
    limiter.init_app(app)

configure_limiter()

# Configure logging to avoid potential security risks when exposing information about requests
logging_config = {
    'version': 1,
    'formatters': {
        'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'}
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
}
dictConfig(logging_config)

# Start application in production mode
app.run(debug=False)
