from flask import Flask, request, jsonify, session
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

app = Flask(__name__)
# Generate a random secret key securely at deployment time (commented out for now)
# app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

# Load SECRET_KEY from environment variable (for development)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Configure email settings using environment variables
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = bool(int(os.environ.get('MAIL_USE_TLS')))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Configure logging with rotation
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(filename='app.log', when='D')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

mail = Mail(app)

# Database configuration (dummy in-memory for simplicity)
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

class TwoFactorCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(10), nullable=False)

def load_credentials():
    try:
        admin_username = os.environ.get('ADMIN_USERNAME') 
        admin_password_hashed = generate_password_hash(os.environ.get('ADMIN_PASSWORD'), work_factor=128000)
        return admin_username, admin_password_hashed
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        raise

def validate_2fa_code(username, code):
    try:
        two_factor_code = TwoFactorCode.query.filter_by(username=username).first()
        if not two_factor_code or two_factor_code.code != code:
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating 2FA code: {e}")
        raise

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not validate_registration_data(data):
            return jsonify({'message': 'Invalid input'}), 400

        # Hash and salt password for secure storage
        password_hashed = generate_password_hash(password, work_factor=128000)
        logger.info(f"User registered: {data}")

        two_factor_code = TwoFactorCode(username=username, code=''.join(secrets.choice(string.digits) for _ in range(10)))
        db.session.add(two_factor_code)
        db.session.commit()

        msg = Message('Registration Successful', sender='your-email@gmail.com', recipients=[username])
        msg.body = 'You have been successfully registered. Please check your email for a 2FA code.'
        mail.send(msg)

        return jsonify({'message': 'User registered successfully'}), 200
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not validate_login_data(data):
            return jsonify({'message': 'Invalid input'}), 400

        admin_username, admin_password_hashed = load_credentials()

        # Directly compare the hash of the provided password to `admin_password_hashed`
        if check_password_hash(admin_password_hashed, data['password']):
            logger.info(f"User logged in: {data}")

            payload = {'username': username}
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

            # Store the 2FA code for verification later
            two_factor_code = TwoFactorCode.query.filter_by(username=username).first()
            session['two_factor_code'] = two_factor_code.code

            return jsonify({'token': token}), 200
        else:
            logger.error(f"Invalid login credentials for user {username}")
            return jsonify({'message': 'Invalid login credentials'}), 401

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    try:
        data = request.json
        username = data.get('username')
        code = data.get('code')

        if not validate_verify_data(data):
            return jsonify({'message': 'Invalid input'}), 400

        # Verify the 2FA code when submitted by the user
        two_factor_code = TwoFactorCode.query.filter_by(username=username).first()
        if two_factor_code and two_factor_code.code == code:
            logger.info(f"User verified: {data}")
            return jsonify({'message': '2FA code verified successfully'}), 200

        logger.error(f"Invalid 2FA code for user {username}")
        return jsonify({'message': 'Invalid 2FA code'}), 401

    except Exception as e:
        logger.error(f"Error during verification: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

def validate_registration_data(data):
    if not data.get('username') or not data.get('password'):
        return False
    return True

def validate_login_data(data):
    if not data.get('username') or not data.get('password'):
        return False
    return True

def validate_verify_data(data):
    if not data.get('username') or not data.get('code'):
        return False
    return True

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
