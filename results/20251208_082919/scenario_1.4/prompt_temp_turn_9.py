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

# Secret key management using environment variables and secure storage (e.g., AWS Secrets Manager or HashiCorp Vault)
secret_key = os.environ['SECRET_KEY']

ph = PasswordHasher(t_cost=16, m_cost=16, p_cost=2)

@app.before_first_request
def init_db():
    try:
        db.create_all()
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        exit(1)

# Implement rate limiting for sensitive endpoints like /login and /protected
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)
protect = limiter.shared_limit("5 per hour") # limit to 5 requests per hour

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
@protect # apply rate limiting for login endpoint
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        user = User.query.filter_by(username=username).first()
        if user and ph.verify(password, user.password):
            token = jwt.encode({'user_id': user.id}, secret_key, algorithm='HS256')
            return jsonify({'token': token})
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Error accessing protected endpoint: {str(e)}")
        return jsonify({'message': 'Failed to access protected endpoint'}), 500

@app.route('/protected', methods=['GET'])
@protect # apply rate limiting for protected endpoint
def protected():
    token = request.headers.get('Authorization')
    try:
        user_id = jwt.decode(token, secret_key, algorithms=['HS256'])['user_id']
        return jsonify({'message': 'Hello, user!'})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
