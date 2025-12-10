from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import smtplib
import secrets
import string
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash, check_reusable_password
from functools import wraps
import logging
import logging.handlers

# Configure logging with rotation
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(filename='app.log', when='D')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

def load_credentials():
    try:
        admin_username = os.environ.get('ADMIN_USERNAME') 
        admin_password_hashed = os.environ.get('ADMIN_PASSWORD_HASHED')
        return admin_username, admin_password_hashed
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        raise

def validate_input(data):
    if not all([data['username'], data['password']]):
        logger.error("Missing username or password")
        return False
    if len(data['username']) < 3 or len(data['password']) < 8:
        logger.error("Username must be at least 3 characters long and password at least 8.")
        return False
    return True

def generate_token(payload):
    try:
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except Exception as e:
        logger.error(f"Error generating JWT token: {e}")
        raise

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not validate_input(data):
            return jsonify({'message': 'Invalid input'}), 400

        admin_username, admin_password_hashed = load_credentials()

        if username != admin_username or generate_password_hash(password) != admin_password_hashed:
            logger.error(f"Invalid login credentials for user {username}")
            return jsonify({'message': 'Invalid login credentials'}), 401

        payload = {'username': username}
        token = generate_token(payload)
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

        if not validate_input(data):
            return jsonify({'message': 'Invalid input'}), 400

        # Hash and salt password for secure storage
        password_hashed = generate_password_hash(password, work_factor=128000)
        logger.info(f"User registered: {data}")
        return jsonify({'message': 'User registered successfully'}), 200
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
