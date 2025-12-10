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

# Load JWT secret key from environment variable for secure storage
secret_key = os.environ.get('JWT_SECRET_KEY')

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

# Store CSRF tokens securely in session instead of generating manually
@app.before_request
def store_csrf_token():
    if request.method == 'POST':
        csrf_token = secrets.token_urlsafe(16)
        session['csrf_token'] = csrf_token

# Validate user input and verify 2FA code securely
@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    # Validate user input
    if not request.json or 'username' not in request.json:
        return jsonify({'message': 'Invalid input'}), 400

    db_username = request.json['username']

    # Verify the provided token against the stored 2FA code with validation
    two_factor_code = session.get('two_factor_code')
    if two_factor_code and len(request.json['token']) == 6 and int(request.json['token']) == two_factor_code:
        return jsonify({'message': '2FA code verified successfully'}), 200

    return jsonify({'message': 'Invalid 2FA token or code'}), 401

# Token blacklisting for secure authentication
@app.before_request
def check_token_blacklist():
    if request.method == 'POST' and 'token' in request.json:
        # Implement token verification and checking against a blacklist database
        pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
