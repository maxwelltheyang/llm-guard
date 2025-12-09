import json
import jwt
import datetime
from flask import Flask, request, jsonify
import os
import bcrypt

app = Flask(__name__)

# Load secret key from environment variable for production use
SECRET_KEY = os.getenv('SECRET_KEY', 'your-256-bit-secret')

# Hardcoded user credentials (for demonstration purposes only)
USERS = {
    "admin": {"password": bcrypt.hashpw("password123".encode(), bcrypt.gensalt())},
    "user": {"password": bcrypt.hashpw("pass456".encode(), bcrypt.gensalt())}
}

def login(username, password):
    if username in USERS:
        hashed_password = USERS[username]["password"]
        if bcrypt.checkpw(password.encode(), hashed_password):
            # Create a JWT token with an expiration time of 1 hour
            payload = {
                'sub': username,
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return token
    return None

@app.route('/login', methods=['POST'])
def login_endpoint():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    token = login(username, password)
    if token:
        return jsonify({'token': token})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(debug=False)
