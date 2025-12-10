from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import smtplib
import secrets
import string
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging
import logging.handlers

# Configure logging with rotation
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.handlers.RotatingFileHandler('app.log', maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

# Use environment variables for sensitive settings or secure storage options (e.g., Hashicorp's Vault or AWS Secrets Manager)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = bool(int(os.environ.get('MAIL_USE_TLS', '1')))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

# Secret key for JWT
secret_key = os.environ.get('SECRET_KEY')

def generate_one_time_code(length=6):
    # Using a cryptographically secure random number generator to avoid potential DoS attacks or edge cases.
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        try:
            # Verify JWT token
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError as e:
            logger.error(f"Token has expired: {e}")
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return jsonify({'message': 'Invalid token'}), 401
    return decorated_function

def load_credentials():
    try:
        admin_username = os.environ.get('ADMIN_USERNAME') 
        admin_password_hashed = os.environ.get('ADMIN_PASSWORD_HASHED')
        return admin_username, admin_password_hashed
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        raise

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.error("Missing username or password")
            return jsonify({'message': 'Missing username or password'}), 400

        admin_username, admin_password_hashed = load_credentials()
        if username != admin_username:
            logger.error("Invalid username")
            return jsonify({'message': 'Invalid username'}), 401

        if not check_password_hash(admin_password_hashed, password):
            logger.error("Invalid password")
            return jsonify({'message': 'Invalid password'}), 401

        # Generate JWT token
        payload = {'username': username}
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        logger.info(f"User logged in: {data}")
        return jsonify({'token': token}), 200
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.error("Missing username or password")
            return jsonify({'message': 'Missing username or password'}), 400

        # Hash and salt password for secure storage
        password_hashed = generate_password_hash(password)
        logger.info(f"User registered: {data}")
        return jsonify({'message': 'User registered successfully'}), 200
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
