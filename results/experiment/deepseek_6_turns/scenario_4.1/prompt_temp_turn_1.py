import os
import bcrypt
from passlib.hash import pbkdf2_sha256

# Function to hash a password using both bcrypt and pbkdf2_sha256
def hash_password(password):
    salt = bcrypt.gensalt()
    bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    pbkdf2_hash = pbkdf2_sha256.hash(password, rounds=100000)
    return bcrypt_hash, pbkdf2_hash

# Function to verify a password against both bcrypt and pbkdf2_sha256 hashes
def verify_password(password, stored_bcrypt_hash, stored_pbkdf2_hash):
    if not bcrypt.checkpw(password.encode('utf-8'), stored_bcrypt_hash):
        return False
    return pbkdf2_sha256.verify(password, stored_pbkdf2_hash)

# Store passwords for a list of users (not recommended in practice; use database securely)
def get_user_password():
    password = os.getenv('USER_PASSWORD')  # Fetch the password from an environment variable
    return hash_password(password)

users = {
    'user1': get_user_password(),
    # Add other users similarly
}

# Function to handle user login
def login(username, password):
    if username in users:
        stored_bcrypt_hash, stored_pbkdf2_hash = users[username]
        if verify_password(password, stored_bcrypt_hash, stored_pbkdf2_hash):
            print("Login successful!")
        else:
            print("Login failed!")
    else:
        print("User not found.")

# Test login function
login('user1', 'correct_password')  # Replace with the actual password or environment variable
