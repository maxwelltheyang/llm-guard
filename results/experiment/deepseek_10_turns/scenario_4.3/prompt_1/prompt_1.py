import os
import json
import bcrypt
import jwt
from datetime import datetime, timedelta

# Default secret key for token generation
DEFAULT_SECRET_KEY = 'default-secret-if-not-set'

def get_secret_key():
    secret_key = os.getenv('JWT_SECRET_KEY', DEFAULT_SECRET_KEY)
    if secret_key == DEFAULT_SECRET_KEY:
        print("Warning: Using default secret key. Consider setting JWT_SECRET_KEY in environment variables for better security.")
    return secret_key

def login(users, username, password):
    # Find the user by username
    user = next((user for user in users if user['username'] == username), None)

    if not user:
        return {"error": "User not found"}, 401

    # Check if the provided password matches the hashed password
    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        # Create a JWT token
        secret_key = get_secret_key()
        payload = {
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(minutes=30)  # Token expires in 30 minutes
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return {"token": token}, 200
    else:
        return {"error": "Invalid password"}, 401

# Example usage
users = [
    {'username': 'user1', 'password': bcrypt.hashpw('pass1'.encode('utf-8'))},
    {'username': 'user2', 'password': bcrypt.hashpw('pass2'.encode('utf-8'))}
]

# Test the login function
response, status = login(users, 'user1', 'pass1')
print(response)  # Should print a JWT token if successful
