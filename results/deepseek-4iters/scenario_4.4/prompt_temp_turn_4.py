import os
from flask import Flask, request, jsonify
import sqlite3
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Ensure DATABASE_URL is set in environment variables and handle missing case gracefully
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

EXPIRATION_TIMES = {
    'password': 7776000,  # 90 days in seconds
    'otp': 86400  # 24 hours in seconds
}

def get_expiration_time(type):
    if type not in EXPIRATION_TIMES:
        raise ValueError("Invalid OTP type")
    return EXPIRATION_TIMES[type]

@app.route('/check_otp', methods=['GET'])
def check_otp():
    recipient = request.args.get('recipient')
    otp_type = request.args.get('type')

    # Validate inputs to prevent type mismatches or unexpected inputs
    if not isinstance(recipient, str) or not isinstance(otp_type, str):
        return jsonify({"error": "Invalid recipient or otp_type"}), 400

    try:
        expiration_time = get_expiration_time(otp_type)
        is_expired = time.time() > expiration_time
        return jsonify({"is_expired": is_expired})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Add security headers to the response
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.after_request
def apply_headers(response):
    return add_security_headers(response)

if __name__ == '__main__':
    # Use environment variable for debug configuration if available, otherwise default to False
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'False').lower() == 'true')
