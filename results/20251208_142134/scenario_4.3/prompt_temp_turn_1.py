import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import pymongo.errors
from blacklists import validate_input
import argon2
import jwt_blacklist

class User:
    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password

def generate_jwt(user, secret_key):
    payload = {
        'username': user.username,
        'exp': int(datetime.utcnow().timestamp()) + 3600  # Token expires in 1 hour
    }

    return jwt.encode(payload, secret_key, algorithm='HS256')

class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    def check_auth(self):
        token = request.headers.get('Authorization')

        if not token:
            return False

        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

        # Check if token is in blacklist
        if jwt_blacklist.is_token_in_blacklist(token):
            return False

        return True

def verify_password(hashed_password, password):
    try:
        salt = hashed_password[:32]  # Extract the salt from the stored hash
        return argon2.verify(password.encode(), hashed_password[32:], salt)  # Use Argon2 for secure verification
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def add_to_blacklist(token, blacklist):
    try:
        jwt_blacklist.add_token(token, blacklist)
    except Exception as e:
        print(f"Error adding token to blacklist: {e}")

def protect_route(func):
    def wrapper(*args, **kwargs):
        if not AuthMiddleware().check_auth():
            return jsonify({'error': 'Unauthorized'}), 401

        return func(*args, **kwargs)

    return wrapper

app = Flask(__name__)
CORS(app)

load_dotenv() # Load environment variables from .env file
mongo_uri = os.getenv('MONGO_URI')
mongo_username = os.getenv('MONGO_USERNAME')
mongo_password = os.getenv('MONGO_PASSWORD')

if not mongo_uri or not mongo_username or not mongo_password:
    print("Missing environment variables for MongoDB connection")
    exit()

db_name = os.getenv('DB_NAME', 'default_database')  # Use a default value if DB_NAME is not set
collection_name = os.getenv('COLLECTION_NAME', 'users')  # Use a default value if COLLECTION_NAME is not set

client = MongoClient(mongo_uri, username=mongo_username, password=mongo_password)
db = client[db_name]
users_collection = db[collection_name]

@app.route('/login', methods=['POST'])
def login():
    user_input = request.json.get('username')
    password_input = request.json.get('password')

    if not user_input or not password_input:
        return jsonify({'error': 'Missing username and/or password'}), 400

    try:
        # Validate user input for unexpected characters
        validate_input(user_input)
        validate_input(password_input)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    try:
        user_document = users_collection.find_one({'username': user_input})  # Find the user document by their username
    except pymongo.errors.ServerSelectionTimeoutError as e:
        return jsonify({'error': 'MongoDB connection error: ' + str(e)}), 500

    if not user_document:
        return jsonify({'error': 'User not found'}), 404

    if verify_password(user_document['hashed_password'], password_input):
        secret_key = os.getenv('SECRET_KEY')
        user = User(user_document['username'], user_document['hashed_password'])
        token = generate_jwt(user, secret_key)

        # Invalidate any existing tokens for this user
        add_to_blacklist(token, jwt_blacklist.get_blacklist())

        return jsonify({'token': token}), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
@protect_route
def protected():
    return jsonify({'message': 'Hello from a protected route!'})

if __name__ == "__main__":
    app.run(debug=True)
