from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
import hashlib
from werkzeug.utils import secure_filename
import logging
from flask_mail import Mail, Message
from functools import wraps
import pytz
from datetime import datetime
import uuid
from argon2 import PasswordHasher
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

if 'DATABASE_URI' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
else:
    # Load configuration from a secure location (e.g., AWS Secrets Manager or HashiCorp Vault)
    from config import Config
    app.config.from_object(Config)

db = SQLAlchemy(app)
mail = Mail(app)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000 * 10, backupCount=1) # Increased log file size to 100MB
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Secret key management using environment variables and secure storage (e.g., AWS Secrets Manager or HashiCorp Vault)
secret_key = os.environ['SECRET_KEY']

ph = PasswordHasher()
@app.before_first_request
def init_db():
    try:
        db.create_all()
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        exit(1)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Not Found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    # Return a generic error message without sensitive information
    return jsonify({'message': 'Internal Server Error'}), 500

# Securely store and manage environment variables (e.g., using AWS Secrets Manager or HashiCorp Vault)
from dotenv import load_dotenv
load_dotenv()

import jwt
secret_key = os.environ['SECRET_KEY']
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        user = User.query.filter_by(username=username).first()
        if user and ph.verify(password, user.password):
            access_token = jwt.encode({'username': username}, secret_key, algorithm='HS256')
            return jsonify({'access_token': access_token.decode('utf-8')})
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({'message': 'Failed to log in'}), 401

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute") # rate limiting for upload endpoint
def upload():
    try:
        file = request.files['file']
        if file.content_length > 1024 * 1024: # 1MB limit
            return jsonify({'message': 'File too large'}), 400
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully'}), 200
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'message': 'Failed to upload file'}), 500

@app.route('/protected', methods=['GET'])
def protected():
    try:
        access_token = request.headers.get('Authorization')
        if not access_token:
            return jsonify({'message': 'Missing Authorization Header'}), 401
        try:
            payload = jwt.decode(access_token, secret_key, algorithms=['HS256'])
            current_user = User.query.filter_by(username=payload['username']).first()
            return jsonify({'message': 'Hello, {}'.format(current_user.username)}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        logger.error(f"Error accessing protected endpoint: {str(e)}")
        return jsonify({'message': 'Failed to access protected endpoint'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

