import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet
from functools import wraps
from werkzeug.security import generate_password_hash
import hashlib
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
limiter = Limiter(
    app,
    key_func=get_remote_address
)

class Config:
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128))
    api_key = db.Column(db.String(128))

def validate_input(data):
    if not isinstance(data, str) or len(data.strip()) == 0:
        raise ValueError('Invalid input')

@app.before_request
def verify_session():
    try:
        user = User.query.filter_by(username=session['username']).first()
        if user is None or user.username != session['username']:
            return 'Unauthorized', 401
    except Exception as e:
        print(f"Error verifying session: {str(e)}")

@app.route('/login', methods=['POST'])
def login():
    try:
        validate_input(request.form.get('username'))
        validate_input(request.form.get('password'))
        user = User.query.filter_by(username=request.form.get('username')).first()
        if not user or not user.api_key == os.environ.get('API_KEY'):
            return 'Invalid API key', 401
        if user.expiration_date and datetime.now() > user.expiration_date:
            return 'API key has expired', 401
        session['username'] = request.form.get('username')
        return 'Logged in successfully'
    except ValueError as e:
        print(f"Error validating input: {str(e)}")
        return str(e), 400
    except Exception as e:
        print(f"Error logging in: {str(e)}")
        return 'Internal server error', 500

@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        return 'Logged out successfully'
    except Exception as e:
        print(f"Error logging out: {str(e)}")

# Enable secure cookies
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Use a more secure secret key for signing sessions
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    print("Secret key is missing, exiting...")
    exit(1)
serializer = URLSafeTimedSerializer(secret_key)

api_key = os.environ.get('API_KEY')
if not api_key:
    print("API key is missing, exiting...")
    exit(1)
Config.API_KEY = api_key

# Set API key expiration date
user = User.query.first()
if user and not user.expiration_date:
    user.expiration_date = datetime.now() + timedelta(days=30)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
