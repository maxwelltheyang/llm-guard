import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt
from pymongo import MongoClient
import pymongo.errors
from blacklists import validate_input
import argon2  # Added library for secure password storage
import jwt_blacklist  # Added library for token blacklisting

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

class SecretsManager:
    def get_secret_key(self):
        load_dotenv() # Load environment variables from .env file
        return os.getenv('SECRET_KEY')

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

# Usage example:

def main():
    try:
        mongo_uri = os.getenv('MONGO_URI')
        mongo_username = os.getenv('MONGO_USERNAME')
        mongo_password = os.getenv('MONGO_PASSWORD')

        if not mongo_uri or not mongo_username or not mongo_password:
            print("Missing environment variables for MongoDB connection")
            return

        db_name = os.getenv('DB_NAME', 'default_database')  # Use a default value if DB_NAME is not set
        collection_name = os.getenv('COLLECTION_NAME', 'users')  # Use a default value if COLLECTION_NAME is not set

        client = MongoClient(mongo_uri, username=mongo_username, password=mongo_password)
        db = client[db_name]
        users_collection = db[collection_name]

        user_input = input("Enter your username: ")
        password_input = input("Enter your password: ")

        if len(user_input) < 1 or len(password_input) < 1:
            print('Username and password must be at least 1 character long')
            return

        try:
            # Validate user input for unexpected characters
            validate_input(user_input)
            validate_input(password_input)
        except Exception as e:
            print(f"Invalid user input: {e}")
            return

        try:
            user_document = users_collection.find_one({'username': user_input})  # Find the user document by their username
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print(f"MongoDB connection error: {e}")
            return

        if user_document is not None:
            if verify_password(user_document['hashed_password'], password_input):
                secret_key = SecretsManager().get_secret_key()
                user = User(user_document['username'], user_document['hashed_password'])
                token = generate_jwt(user, secret_key)
                print(f"Generated JWT: {token}")
                # Token will be invalidated after login
            else:
                add_to_blacklist(token, jwt_blacklist.get_blacklist())  # Invalidate any existing tokens for this user
                print('Invalid credentials')
        else:
            print('User not found')

    except pymongo.errors.ConnectionFailure as e:
        print(f"MongoDB connection error: {e}")

if __name__ == "__main__":
    main()
