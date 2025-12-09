from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, login_required, current_user, current_app, \
    RegisterForm, StringField, PasswordField, Required
import os
from dotenv import load_dotenv
import logging.config
from logging.handlers import RotatingFileHandler
from functools import wraps
import hashlib
from secrets import token_urlsafe
from password_strength import PasswordStats
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import string
import random

app = Flask(__name__)
load_dotenv()

# Set debug mode based on environment variables or configuration files
debug_mode = os.environ.get('DEBUG')
if not isinstance(debug_mode, bool):
    if debug_mode.lower() == 'true':
        debug_mode = True
    else:
        debug_mode = False

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# API Key Generation and Revocation
api_key_store = {}

def generate_api_key(user_id):
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    api_key_store[user_id] = key
    return key

def revoke_api_key(user_id):
    if user_id in api_key_store:
        del api_key_store[user_id]

# User Authentication and Password Hashing
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)  
    password_hash = db.Column(db.String(255))  

class LoginForm(RegisterForm):
    class Meta:
        fields = ('email', 'password')

def validate_input(data):
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    password_length = 8 <= len(data['password']) <= 128
    if not re.match(email_pattern, data['email']):
        return False
    if not password_length:
        return False
    return True

def validate_api_key(key):
    key_length = 32 <= len(key) <= 64
    if not key_length or not all(c.isalnum() for c in key):
        return False
    return True

# Error Handling
@app.errorhandler(403)
def forbidden_error(e):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(422)
def unprocessable_entity_error(e):
    return jsonify({'error': 'Unprocessable Entity'}), 422

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error'}), 500

@app.errorhandler(404)
def not_found_error(e):
    return jsonify({'error': 'Not Found'}), 404

# API Key Validation
@app.before_request
def validate_api_key():
    jwt_token = request.headers.get('Authorization').split()[1]
    payload = jwt.decode_token(jwt_token)
    user_id = payload['identity']
    api_key = api_key_store.get(user_id)
    if not api_key or not validate_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 401

if __name__ == '__main__':
    if not debug_mode:
        from waitress import serve
        bind_ip = os.environ.get('BIND_IP')
        serve(app, host=bind_ip, port=5000)

# JWT Configuration
jwt = JWTManager()

def get_jwt_identity():
    jwt_token = request.headers.get('Authorization').split()[1]
    payload = jwt.decode_token(jwt_token)
    return payload['identity']

@app.route('/users', methods=['GET'])
@jwt_required
def get_users():
    user_id = get_jwt_identity()
    # Return all users, excluding the current user
    pass

# Input Validation
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not validate_input(data):
        return jsonify({'error': 'Invalid input'}), 422
    new_user = User(email=data['email'], password_hash=bcrypt.generate_password_hash(data['password']))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'api_key': generate_api_key(new_user.id)}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    if not validate_input(data):
        return jsonify({'error': 'Invalid input'}), 422
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        api_key = generate_api_key(user.id)
        return jsonify({'api_key': api_key}), 200
    return jsonify({'error': 'Invalid credentials'}), 401
