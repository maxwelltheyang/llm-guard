import os
from flask import Flask, request, jsonify
import sqlite3
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database connection string stored in environment variable for security
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

EXPIRATION_TIMES = {
    'password': 7776000,  # 90 days in seconds
    'otp': 3600  # 1 hour in seconds
}

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def is_otp_expired(recipient, otp_type):
    if otp_type not in EXPIRATION_TIMES:
        raise ValueError("Invalid OTP type")

    expiration_time = EXPIRATION_TIMES[otp_type]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM otps WHERE recipient=? AND type=?", (recipient, otp_type))
    result = cursor.fetchone()
    if not result:
        return True  # OTP expired as no record found

    stored_timestamp = result[0]
    return stored_timestamp + expiration_time < time.time()

@app.route('/check-otp', methods=['GET'])
def check_otp():
    recipient = request.args.get('recipient')
    otp_type = request.args.get('type')

    # Validate inputs to prevent type mismatches or unexpected inputs
    if not isinstance(recipient, str) or not isinstance(otp_type, str):
        return jsonify({"error": "Invalid recipient or otp_type"}), 400

    try:
        is_expired = is_otp_expired(recipient, otp_type)
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
    app.run(host='0.0.0.0', port=5000)
