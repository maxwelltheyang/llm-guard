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
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({'error': 'Invalid email or password'}), 401

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
@jwt_required
def revoke():
    user_id = get_jwt_identity()
    revoke_api_key(user_id)
    return jsonify({'message': 'API key revoked'}), 200

if __name__ == '__main__':
    if not debug_mode:
        from waitress import serve
        bind_ip = os.environ.get('BIND_IP')
        serve(app, host=bind_ip, port=5000)

# JWT Configuration
jwt = JWTManager()

def validate_input(data):
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True

def get_jwt_identity():
    jwt_token = request.headers.get('Authorization').split()[1]
    payload = jwt.decode_token(jwt_token)
    return payload['identity']

# Error Handling
@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error'}), 500

@app.errorhandler(404)
def not_found_error(e):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(401)
def unauthorized_error(e):
    return jsonify({'error': 'Unauthorized'}), 401
