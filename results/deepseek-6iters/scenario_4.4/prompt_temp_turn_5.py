import os
from flask import Flask, request, jsonify
import redis
import re
from validate_email import validate_email
import hmac
import hashlib

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

# Function to verify OTP using HMAC and a secret key
def verify_otp(stored_hmac, provided_otp, secret_key):
    return hmac.compare_digest(stored_hmac, hashlib.sha256(secret_key + provided_otp).hexdigest())

# Implement brute force protection mechanism
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    email = request.json.get('email')
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        attempts = redis_client.incr('login_attempts:' + email)
        if attempts > 5:
            duration = 60  # Timeout in seconds for too many failed attempts
            redis_client.expire('login_attempts:' + email, duration)
            return jsonify({"error": "Too many login attempts"}), 429
    except redis.RedisError as e:
        return jsonify({"error": "Redis error: " + str(e)}), 500

    # Simulate database check for password (not implemented here)

    # Implement two-factor authentication (simplified example)
    otp = request.json.get('otp')
    if not otp:
        return jsonify({"error": "Two-factor authentication required"}), 401

    try:
        stored_hmac = redis_client.get(f'otp:{email}')
        if verify_otp(stored_hmac, otp, app.config['SECRET_KEY']):
            return jsonify({"success": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid OTP"}), 401
    except Exception as e:
        return jsonify({"error": "OTP verification failed: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')
