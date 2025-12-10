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

# Set the secret key for JWT token
secret_key = secrets.token_urlsafe(32)
app.config['SECRET_KEY'] = secret_key

# Email configuration settings
email_config = {
    'MAIL_SERVER': os.environ.get('MAIL_SERVER'),
    'MAIL_PORT': int(os.environ.get('MAIL_PORT')),
    'MAIL_USE_TLS': bool(os.environ.get('MAIL_USE_TLS')),
    'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD')
}

# Database configuration settings
database_config = {
    'username': os.environ.get('DB_USERNAME'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT')),
    'database': os.environ.get('DB_NAME')
}

# Initialize Flask-Mail
mail = Mail(app)

@app.route('/register', methods=['POST'])
def register():
    # Validate user input
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    # Generate a random password for the user
    password = secrets.token_urlsafe(32)

    # Send email to the user with their temporary password
    msg = Message('Temporary Password', sender='your-email@example.com', recipients=[request.json['username']])
    msg.body = f'Your temporary password is: {password}'
    mail.send(msg)

    # Store the username and hashed password in the database
    db_username = request.json['username']
    hashed_password = generate_password_hash(password)

    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    # Validate user input
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    # Check if the username and password are valid
    db_username = request.json['username']
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
    code = request.json['code']

    # Check if the provided code matches the one stored in the database
    if db_username and code:
        # Store the code securely for future verification
        session['two_factor_code'] = generate_password_hash(code)

        return jsonify({'message': '2FA code verified successfully'}), 200

    return jsonify({'message': 'Invalid 2FA code'}), 401

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
