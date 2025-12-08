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

# User Authentication and Password Hashing
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)  
    password_hash = db.Column(db.String(255))  

class LoginForm(RegisterForm):
    class Meta:
        fields = ('email', 'password')

# Database Configuration and Connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def check_password(password, hashed_password):
    max_work_factor = 12
    return bcrypt.check_password_hash(hashed_password, password=password, max_work_factor=max_work_factor)

# API Key and User Management
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)  
    api_key = db.Column(db.String(255), unique=True)  

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password(password, user.password_hash):
        return jsonify({'api_key': user.api_key}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')

    if not validate_input(request.json):
        return jsonify({'error': 'Missing required fields'}), 400

    new_user = User(email=email, password_hash=bcrypt.generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'api_key': generate_api_key(new_user.id)}), 201

@app.route('/revoke', methods=['POST'])
@login_required
def revoke():
    user_id = current_user.id
    revoke_api_key(user_id)
    return jsonify({'message': 'API key revoked'}), 200

if __name__ == '__main__':
    if not debug_mode:
        from waitress import serve
        bind_ip = os.environ.get('BIND_IP')
        serve(app, host=bind_ip, port=5000)
