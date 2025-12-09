import os
from flask import Flask, request, jsonify
import redis
import re
from validate_email import validate_email

app = Flask(__name__)
redis_client = redis.StrictRedis()

# Update the email validation function with a more comprehensive regex
def is_valid_email(email):
    if not validate_email(email, verify=True):
        return False
    # Additional regex to check for valid format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True

# Middleware to ensure HTTPS is used in production
@app.before_request
def require_https():
    if not request.is_secure:
        return jsonify({"error": "HTTPS required"}), 403

# Set the secret key from an environment variable
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or 'default-secret-key'

# Login flow with basic security measures
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Implement brute force protection (simplified example)
    if redis_client.incr('login_attempts:' + email) > 5:
        return jsonify({"error": "Too many login attempts"}), 429

    # Simulate database check for password (not implemented here)

    # Implement two-factor authentication (simplified example)
    if not request.json.get('otp'):
        return jsonify({"error": "Two-factor authentication required"}), 401

    # Verify OTP using HMAC with the secret key from environment variable
    stored_hmac = redis_client.get(f'otp:{email}')
    if verify_otp(stored_hmac, request.json['otp'], app.config['SECRET_KEY']):
        return jsonify({"success": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 401

    # Additional security measures can be added here (e.g., rate limiting, captchas)

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')
