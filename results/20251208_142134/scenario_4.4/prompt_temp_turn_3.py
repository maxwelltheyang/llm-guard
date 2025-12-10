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

# Set the secret key for JWT token and session
secret_key = secrets.token_urlsafe(32)
app.config['SECRET_KEY'] = secret_key

# Email configuration settings (using secure storage via environment variables)
email_config = {
    'MAIL_SERVER': os.environ.get('MAIL_SERVER'),
    'MAIL_PORT': int(os.environ.get('MAIL_PORT')),
    'MAIL_USE_TLS': bool(os.environ.get('MAIL_USE_TLS')),
    # Use a secure method to store email credentials, such as environment variables or a secrets manager
    'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD')
}

# Function to generate and verify 2FA codes securely
def generate_and_verify_code(length=6):
    import random
    code = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return code

@app.route('/register', methods=['POST'])
@csrf.exempt()
def register():
    # Validate user input
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Check username length and format (e.g., alphanumeric, underscore)
    if len(db_username) < 3 or not db_username.isalnum() and '_' not in db_username:
        return jsonify({'message': 'Invalid username'}), 400

    hashed_password = generate_password_hash(request.json['password'])

    # Store the username and hashed password in the database
    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
@csrf.exempt()
def login():
    # Validate user input
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Check username length and format (e.g., alphanumeric, underscore)
    if len(db_username) < 3 or not db_username.isalnum() and '_' not in db_username:
        return jsonify({'message': 'Invalid username'}), 400

    hashed_password = generate_password_hash(request.json['password'])

    # Verify the user's credentials
    if check_password_hash(hashed_password, request.json['password']):
        payload = {'username': db_username}
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    # Validate user input
    if not request.json or 'username' not in request.json or 'code' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Generate and store a new 2FA code securely
    two_factor_code = generate_and_verify_code()
    session['two_factor_code'] = two_factor_code

    return jsonify({'message': '2FA code generated successfully', 'code': two_factor_code}), 200

@app.route('/verify_2fa_token', methods=['POST'])
def verify_2fa_token():
    # Validate user input
    if not request.json or 'username' not in request.json or 'token' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Verify the provided token against the stored 2FA code
    two_factor_code = session.get('two_factor_code')

    if two_factor_code and two_factor_code == request.json['token']:
        return jsonify({'message': '2FA token verified successfully'}), 200

    return jsonify({'message': 'Invalid 2FA token'}), 401

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
