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

# Error handling for Redis operations
def handle_redis_error(e):
    return jsonify({"error": "Redis error: " + str(e)}), 500

# Implement brute force protection with a timeout on the incremented value
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        attempts = redis_client.incr('login_attempts:' + email)
        if attempts > 5:
            duration = 60  # Timeout in seconds for too many failed attempts
            redis_client.expire('login_attempts:' + email, duration)
            return jsonify({"error": "Too many login attempts"}), 429
    except redis.RedisError as e:
        handle_redis_error(e)

    # Simulate database check for password (not implemented here)

    # Implement two-factor authentication (simplified example)
    if not request.json.get('otp'):
        return jsonify({"error": "Two-factor authentication required"}), 401

    try:
        stored_hmac = redis_client.get(f'otp:{email}')
        if verify_otp(stored_hmac, request.json['otp'], app.config['SECRET_KEY']):
            return jsonify({"success": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid OTP"}), 401
    except Exception as e:
        return jsonify({"error": "OTP verification failed: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')
