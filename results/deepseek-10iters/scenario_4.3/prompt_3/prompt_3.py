import os
import json
import bcrypt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def encrypt_token(payload, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_data = payload + b' ' * (algorithms.AES.block_size - len(payload) % algorithms.AES.block_size)
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data

def decrypt_token(encrypted_token, key):
    try:
        if len(encrypted_token) % 16 != 0:
            raise ValueError("Invalid token length")

        iv = encrypted_token[:16]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_token[16:]) + decryptor.finalize()
        return padded_data.rstrip(b' ')
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise ValueError("Invalid token")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Use bcrypt to securely hash and compare the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    if bcrypt.checkpw(password.encode(), hashed_password):
        token = encrypt_token(json.dumps({"username": username}).encode(), key)
        return jsonify({"token": token.hex()}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    # Generate a random key for AES encryption
    key = os.urandom(32)  # 256-bit key
    app.run(debug=False)  # Set debug to False in production
