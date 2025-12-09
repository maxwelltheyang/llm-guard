from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as uts
import os

app = Flask(__name__)
# Use a secure environment variable for the secret key.
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

bcrypt = Bcrypt(app)
app.config['BCRYPT_WORK_FACTOR'] = 13

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # For demonstration purposes, assume we have a user with the provided credentials.
    if username == 'test' and hash_password(password) == bcrypt.generate_password_hash('hashed_password').decode('utf-8'):
        session['token'] = generate_jwt_token(1)
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/protected', methods=['GET'])
def protected():
    # Check if the user is logged in and has a valid JWT token.
    try:
        payload = jwt.decode(session['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({"message": f"Welcome, User {payload['user_id']}"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

@app.route('/logout', methods=['GET'])
def logout():
    session['token'] = None
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    # Set debug=False in production environments.
    app.run(debug=True)
