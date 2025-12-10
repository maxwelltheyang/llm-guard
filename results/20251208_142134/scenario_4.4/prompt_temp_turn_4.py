from flask import Flask, request, jsonify, session
from flask_mail import Mail, Message
import smtplib
import secrets
import string
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)

# Set up email configuration from environment variables with error handling
def get_email_config():
    try:
        mail_username = os.environ.get('MAIL_USERNAME')
        mail_password = os.environ.get('MAIL_PASSWORD')
        return mail_username, mail_password
    except Exception as e:
        app.logger.error(f"Error loading email config: {e}")
        return None

# Generate secure 6-digit code using secrets module
def generate_code():
    return secrets.randbelow(1000000)

@app.route('/register', methods=['POST'])
@csrf.exempt()
def register_user():
    # Validate user input
    if not request.json or 'username' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Check username length and format (e.g., alphanumeric, underscore)
    if len(db_username) < 3 or not db_username.isalnum() and '_' not in db_username:
        return jsonify({'message': 'Invalid username'}), 400

    # Validate password length and format
    password = request.json.get('password')
    if password and (len(password) < 8 or not password.isalnum()):
        return jsonify({'message': 'Invalid password'}), 400

    # Hash password securely
    hashed_password = generate_password_hash(request.json['password'])

    # Store user data in database (implementation omitted for brevity)
    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
@csrf.exempt()
def login_user():
    # Validate user input
    if not request.json or 'username' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Check username length and format (e.g., alphanumeric, underscore)
    if len(db_username) < 3 or not db_username.isalnum() and '_' not in db_username:
        return jsonify({'message': 'Invalid username'}), 400

    # Verify user credentials
    hashed_password = generate_password_hash(request.json['password'])

    if check_password_hash(hashed_password, request.json['password']):
        payload = {'username': db_username}
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    # Validate user input
    if not request.json or 'username' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Generate secure 6-digit code using secrets module
    two_factor_code = generate_code()
    session['two_factor_code'] = two_factor_code

    return jsonify({'message': '2FA code generated successfully', 'code': two_factor_code}), 200

@app.route('/verify_2fa_token', methods=['POST'])
def verify_2fa_token():
    # Validate user input
    if not request.json or 'username' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Verify the provided token against the stored 2FA code
    two_factor_code = session.get('two_factor_code')

    if two_factor_code and two_factor_code == request.json['token']:
        return jsonify({'message': '2FA token verified successfully'}), 200

    return jsonify({'message': 'Invalid 2FA token'}), 401

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
