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
        except jwt.ExpiredSignatureError as e:
            import logging
            logging.error(f"Token expired: {e}")
            return False
        except jwt.InvalidTokenError as e:
            import logging
            logging.error(f"Invalid token: {e}")
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
        import logging
        logging.error(f"Error verifying password: {e}")
        return False

def add_to_blacklist(token, blacklist):
    try:
        jwt_blacklist.add_token(token, blacklist)
    except Exception as e:
        import logging
        logging.error(f"Error adding token to blacklist: {e}")

def protect_route(func):
    def wrapper(*args, **kwargs):
        if not AuthMiddleware().check_auth():
            return jsonify({'error': 'Unauthorized'}), 401

        return func(*args, **kwargs)

    return wrapper

import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

app = Flask(__name__)
CORS(app)

load_dotenv() # Load environment variables from .env file

# Validate required environment variables are present
required_env_vars = ['MONGO_URI', 'MONGO_USERNAME', 'MONGO_PASSWORD']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

mongo_uri = os.getenv('MONGO_URI')
mongo_username = os.getenv('MONGO_USERNAME')
try:
    mongo_password = os.getenv('MONGO_PASSWORD')
except Exception as e:
    import logging
    logging.error(f"Error retrieving MONGO_PASSWORD from environment variables: {e}")
    exit()

if not mongo_uri or not mongo_username or not mongo_password:
    import logging
    logging.error("Missing environment variables for MongoDB connection")
    exit()

db_name = os.getenv('DB_NAME', 'default_database')  # Use a default value if DB_NAME is not set
collection_name = os.getenv('COLLECTION_NAME', 'users')  # Use a default value if COLLECTION_NAME is not set

try:
    client = MongoClient(mongo_uri, username=mongo_username, password=mongo_password)
except pymongo.errors.OperationFailure as e:
    import logging
    logging.error(f"Error connecting to MongoDB: {e}")
    exit()

db = client[db_name]
users_collection = db[collection_name]

# Production settings
if __name__ == "__main__":
    app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG'))
    ssl_context = context
    ip_address = 'your_server_ip' # replace with your server's IP address or use host='localhost'
    try:
        app.run(host=ip_address, port=5000)
    except Exception as e:
        import logging
        logging.error(f"Error running Flask application: {e}")
