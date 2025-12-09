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
    # Additional regex to check for valid email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return True
    else:
        return False

# HTTPS enforcement middleware
@app.before_request
def require_https():
    if not request.is_secure:
        return jsonify({"error": "HTTPS required"}), 403

# Error handling for Redis operations
try_limit = 5
timeout_duration = 60  # Timeout in seconds for too many failed attempts

def handle_redis_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.RedisError as e:
            return jsonify({"error": "Redis error: " + str(e)}), 500
    return wrapper

@handle_redis_errors
def incr_login_attempts(email):
    attempts = redis_client.incr('login_attempts:' + email)
    if attempts == try_limit:
        redis_client.expire('login_attempts:' + email, timeout_duration)
    return attempts

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    attempts = incr_login_attempts(email)
    if attempts > try_limit:
        return jsonify({"error": "Too many login attempts"}), 429

    # Simulate database check for password (not implemented here)

    # Implement two-factor authentication (simplified example)
    otp = request.json.get('otp')
    if not otp:
        return jsonify({"error": "Two-factor authentication required"}), 401

    stored_hmac = redis_client.get(f'otp:{email}')
    if verify_otp(stored_hmac, otp):
        return jsonify({"success": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 401

def verify_otp(stored_hmac, otp):
    if stored_hmac and hmac.compare_digest(stored_hmac.decode(), hashlib.sha256(otp.encode()).hexdigest()):
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')
