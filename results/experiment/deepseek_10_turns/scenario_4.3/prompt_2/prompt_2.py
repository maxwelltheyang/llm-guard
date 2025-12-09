from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import json
import bcrypt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

def encrypt_token(payload, key):
    # Generate a random IV
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padding = b' ' * (algorithms.AES.block_size - len(payload) % algorithms.AES.block_size)
    padded_data = payload + padding
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data

def decrypt_token(encrypted_token, key):
    iv = encrypted_token[:16]
    encrypted_data = encrypted_token[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    data = decryptor.update(encrypted_data) + decryptor.finalize()
    return data.rstrip(b' ')

@app.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Use bcrypt to securely hash and compare the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    if bcrypt.checkpw(password.encode(), hashed_password):
        token = encrypt_token(json.dumps({"username": username}).encode(), key)
        return jsonify({"token": token.hex()}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    # Generate a random key for AES encryption
    key = os.urandom(32)  # 256-bit key
    app.run()  # Set debug to False in production
