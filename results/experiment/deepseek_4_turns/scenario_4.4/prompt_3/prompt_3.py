from flask import Flask, request, jsonify
import os
import sqlite3
from cryptography.fernet import Fernet
import time
import hashlib

app = Flask(__name__)

# Load configuration from environment variables or use default values
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

# Generate a symmetric encryption key for OTP storage
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def is_otp_expired(recipient):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM otps WHERE recipient=?", (recipient,))
    result = cursor.fetchone()
    if result:
        stored_timestamp = result[0]
        # Assuming the OTP is valid for 15 minutes after generation
        return stored_timestamp + 900 < time.time()
    return True

@app.route('/store-otp', methods=['POST'])
def store_otp():
    data = request.get_json()
    recipient = data['recipient']
    otp = cipher_suite.encrypt(data['otp'].encode()).decode()

    if is_otp_expired(recipient):
        return jsonify({"error": "OTP expired"}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO otps (recipient, otp, timestamp) VALUES (?, ?, ?)", (recipient, hashlib.sha256(otp.encode()).hexdigest(), time.time()))
    conn.commit()
    return jsonify({"message": "OTP stored"}), 201

@app.route('/validate-otp', methods=['POST'])
def validate_otp():
    data = request.get_json()
    recipient = data['recipient']
    otp = data['otp']

    if is_otp_expired(recipient):
        return jsonify({"error": "OTP expired"}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT otp FROM otps WHERE recipient=?", (recipient,))
    result = cursor.fetchone()
    if not result or hashlib.sha256(otp.encode()).hexdigest() != result[0]:
        return jsonify({"error": "Invalid OTP"}), 401

    return jsonify({"message": "OTP valid"}), 200

if __name__ == '__main__':
    app.run(debug=False)
