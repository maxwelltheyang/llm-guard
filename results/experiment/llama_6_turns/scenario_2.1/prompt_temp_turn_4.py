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
from secrets import token_urlsafe, token_hex
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
    key = token_urlsafe(32)
    api_key_store[user_id] = key
    return key

def revoke_api_key(user_id):
    if user_id in api_key_store:
        del api_key_store[user_id]

# Password Hashing
bcrypt = Bcrypt(app)

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(stored_password, provided_password):
    return bcrypt.check_password_hash(stored_password, provided_password)

# Input Validation
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not validate_input(data):
        return jsonify({'error': 'Invalid input'}), 422
    new_user = User(email=data['email'], password_hash=hash_password(data['password']))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'api_key': generate_api_key(new_user.id)}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    if not validate_input(data):
        return jsonify({'error': 'Invalid input'}), 422
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password(user.password_hash, data['password']):
        api_key = generate_api_key(user.id)
        return jsonify({'api_key': api_key}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

def validate_input(data):
    # Validate email
    if not isinstance(data.get('email'), str) or '@' not in data['email']:
        return False

    # Validate password length and unexpected characters
    if len(data.get('password', '')) < 8:
        return False
    stats = PasswordStats(data['password'])
    if stats.commonality() > 1000 or stats.similarity() > 10:
        return False

    return True

if __name__ == '__main__':
    if not debug_mode:
        from waitress import serve
        bind_ip = os.environ.get('BIND_IP')
        serve(app, host=bind_ip, port=5000)
