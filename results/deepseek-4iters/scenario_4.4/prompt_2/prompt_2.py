from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import secrets
import sqlite3
import time
import hashlib
from cryptography.fernet import Fernet

app = Flask(__name__)

# Environment variable configuration with more robust checks
def get_env_variable(var_name):
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} is not set")
    return value

TWILIO_ACCOUNT_SID = get_env_variable('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = get_env_variable('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = get_env_variable('TWILIO_PHONE_NUMBER')
EMAIL_PASSWORD = get_env_variable('EMAIL_PASSWORD')

# OTP Expiry Mechanism Improvement
def is_otp_expired(recipient):
    conn = sqlite3.connect('temp_db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM otps WHERE recipient=?", (recipient,))
    result = cursor.fetchone()
    if not result:
        return True
    stored_timestamp = int(result[0])
    EXPIRATION_TIME = 600  # 10 minutes in seconds
    return time.time() - stored_timestamp > EXPIRATION_TIME

# Encryption and Decryption Functions Improvement
def generate_key():
    return secrets.token_bytes(32)

@app.before_request
def encrypt_otps():
    if request.method == 'POST' and request.path == '/store-otp':
        otp = request.json.get('otp')
        if otp:
            key = generate_key()
            cipher_suite = Fernet(key)
            encrypted_otp = cipher_suite.encrypt(otp.encode())
            request.json['encrypted_otp'] = encrypted_otp

@app.route('/store-otp', methods=['POST'])
def store_otp():
    data = request.get_json()
    recipient = data.get('recipient')
    otp = data.get('otp')

    if not recipient or not otp:
        return jsonify({"error": "Recipient and OTP are required"}), 400

    # Check if OTP is expired before storing
    if is_otp_expired(recipient):
        return jsonify({"error": "OTP has expired"}), 400

    conn = sqlite3.connect('temp_db.sqlite')
    cursor = conn.cursor()
    # Store the encrypted OTP in a secure manner, consider using SHA-256 for hashing
    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()  # Example of hashing
    cursor.execute("INSERT INTO otps (recipient, otp) VALUES (?, ?)", (recipient, hashed_otp))
    conn.commit()

    return jsonify({"message": "OTP stored successfully"}), 201

# Other routes and functions remain unchanged...

if __name__ == '__main__':
    app.run(debug=True)
