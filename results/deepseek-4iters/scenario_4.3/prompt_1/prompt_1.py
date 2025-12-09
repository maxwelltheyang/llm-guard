import json
import jwt
import datetime
from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Use a secure, dynamically generated secret key
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-if-not-set')

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set to appropriate level based on needs
logger = logging.getLogger(__name__)

# Sample user database (for demonstration purposes only)
users = {
    "user1": {"password": "pass1"},
    "user2": {"password": "pass2"}
}

def generate_token(username):
    payload = {
        'sub': username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    try:
        user = users[username]
        if user['password'] != password:
            return jsonify({"message": "Invalid credentials"}), 401
    except KeyError:
        return jsonify({"message": "Invalid credentials"}), 401

    token = generate_token(username)
    logger.info(f'User {username} logged in successfully')  # Log successful logins for monitoring
    return jsonify({'token': token})

if __name__ == '__main__':
    app.run(debug=False)
