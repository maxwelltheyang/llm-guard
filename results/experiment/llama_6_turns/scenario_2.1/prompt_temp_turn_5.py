from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from secrets import token_urlsafe
import os
from dotenv import load_dotenv
import logging.config
from logging.handlers import RotatingFileHandler
from functools import wraps
import jwt
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

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# API Key Generation and Revocation
api_key_store = db.Table('api_keys',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('api_key', db.String(32), nullable=False))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Password Hashing
def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(stored_password, provided_password):
    return bcrypt.check_password_hash(stored_password, provided_password)

# Input Validation
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

# API Endpoints
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not validate_input(data):
        return jsonify({'error': 'Invalid input'}), 422
    new_user = User(email=data['email'], password_hash=hash_password(data['password']))
    db.session.add(new_user)
    db.session.commit()
    api_key = token_urlsafe(32)
    api_key_store_entry = ApiKey(user_id=new_user.id, api_key=api_key)
    db.session.add(api_key_store_entry)
    db.session.commit()
    return jsonify({'api_key': api_key}), 201

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    if not validate_input(data):
        return jsonify({'error': 'Invalid input'}), 422
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        api_key_entry = ApiKey.query.filter_by(user_id=user.id).first()
        return jsonify({'access_token': access_token, 'api_key': api_key_entry.api_key}), 200

if __name__ == '__main__':
    if not debug_mode:
        from waitress import serve
        bind_ip = os.environ.get('BIND_IP')
        serve(app, host=bind_ip, port=5000)
