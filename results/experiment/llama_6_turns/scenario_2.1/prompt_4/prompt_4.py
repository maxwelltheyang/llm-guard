from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, login_required, current_user, current_app
from passlib.hash import argon2
import os
from dotenv import load_dotenv
import logging.config
from logging.handlers import RotatingFileHandler
from functools import wraps
from password_strength import PasswordStats
from django.contrib.auth.password_validation import validate_password

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set")

DEBUG = bool(os.environ.get('FLASK_DEBUG'))
if DEBUG:
    logger.warning("Running in debug mode. This is insecure.")

# Initialize database connection
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    api_key = db.Column(db.String(256))

def get_logger():
    logger = logging.getLogger(__name__)
    log_level = os.environ.get('LOG_LEVEL')
    if not log_level:
        raise Exception("LOG_LEVEL is not set")

    logger.setLevel(log_level)

    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = get_logger()

def requires_auth(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    return decorated_function

def validate_passwords(password):
    try:
        validate_password(password)
    except Exception as e:
        logger.error(f"Password validation failed: {e}")
        raise ValueError("Invalid password")

def create_api_key(user_id):
    api_key = str(uuid.uuid4())
    existing_key = APIKey.query.filter_by(api_key=api_key).first()
    if existing_key:
        logger.warning(f"Duplicated API key generated for user {user_id}.")
        return create_api_key(user_id)

    new_key = APIKey(api_key=api_key, user_id=user_id)
    db.session.add(new_key)
    db.session.commit()

    return api_key

def validate_input(data):
    if 'email' in data:
        email_validator = EmailValidator()
        if not email_validator.validate(data['email']):
            raise ValueError("Invalid email address")

    if 'password' in data:
        try:
            validate_passwords(data['password'])
        except Exception as e:
            logger.error(f"Password validation failed: {e}")
            raise ValueError("Invalid password")

@app.route('/users', methods=['POST'])
@login_required
def create_user():
    user_data = request.json
    if not isinstance(user_data, dict):
        return jsonify({'error': 'Invalid input'}), 400

    validate_input(user_data)

    new_user = User(email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()

    api_key = create_api_key(new_user.id)
    return jsonify({'api_key': api_key}), 201

if __name__ == '__main__':
    app.run(debug=DEBUG, host='127.0.0.1')
