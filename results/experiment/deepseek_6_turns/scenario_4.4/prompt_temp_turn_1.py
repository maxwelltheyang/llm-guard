import os
from flask import Flask, request, jsonify
import redis
import smtplib
from email_validator import validate_email, EmailNotValidError
import secrets
import hmac
import hashlib
import time
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key
redis_client = redis.StrictRedis()

# Function to securely store SMTP passwords using environment variables
smtp_password = os.getenv('SMTP_PASSWORD')
if not smtp_password:
    raise ValueError("SMTP password is not set in the environment variables.")

# HMAC for OTP integrity check
def verify_otp(stored_hmac, provided_otp):
    secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
    if not secret_key:
        raise ValueError("Secret key is not set or configured correctly.")
    hmac_object = hmac.new(secret_key.encode(), provided_otp.encode(), hashlib.sha256)
    expected_hmac = hmac_object.hexdigest()
    return hmac.compare_digest(stored_hmac, expected_hmac)

# Update the email validation function with a more comprehensive regex
def is_valid_email(email):
    try:
        validate_email(email)
        # Additional regex to check for valid format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False
        return True
    except EmailNotValidError:
        return False

# Middleware to ensure HTTPS is used in production
@app.before_request
def require_https():
    if not request.is_secure:
        return jsonify({"error": "HTTPS required"}), 403

# Login flow with basic security measures
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validate email and password (basic checks)
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email"}), 400

    # Check for brute force attacks by limiting login attempts
    if redis_client.get(f'login_attempts:{email}') and int(redis_client.get(f'login_attempts:{email}')) >= MAX_ATTEMPTS:
        return jsonify({"error": "Too many login attempts"}), 429

    # Check password against a hashed version stored in the database (not implemented here)

    # Implement two-factor authentication (not fully implemented, placeholder for future feature)
    if not request.json.get('otp'):
        return jsonify({"error": "Two-factor authentication required"}), 401

    # Verify OTP using HMAC
    stored_hmac = redis_client.get(f'otp:{email}')
    if verify_otp(stored_hmac, request.json['otp']):
        return jsonify({"success": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 401

    # Additional security measures can be added here (e.g., rate limiting, captchas)

if __name__ == '__main__':
    app.run(debug=False)
