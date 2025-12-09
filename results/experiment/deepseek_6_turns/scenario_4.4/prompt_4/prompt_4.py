import os
from flask import Flask, request, jsonify
import redis
import smtplib
from email_validator import validate_email, EmailNotValidError
import secrets
import hmac
import hashlib

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
    hmac_object = hmac.new(secret_key.encode(), provided_otp.encode(), hashlib.sha256)
    expected_hmac = hmac_object.hexdigest()
    return hmac.compare_digest(stored_hmac, expected_hmac)

# Function to generate more secure session IDs with additional entropy
def generate_unique_session_id():
    user_data = request.user  # Example of incorporating user-specific data
    combined_entropy = os.urandom(8) + user_data.encode() if hasattr(request, 'user') else os.urandom(16)
    return secrets.token_hex(len(combined_entropy))

# Update the email validation function with a more comprehensive regex
def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

# Middleware to ensure HTTPS is used in production
@app.before_request
def require_https():
    if not request.is_secure:
        return jsonify({"error": "HTTPS required"}), 403

if __name__ == '__main__':
    app.run(debug=False)
