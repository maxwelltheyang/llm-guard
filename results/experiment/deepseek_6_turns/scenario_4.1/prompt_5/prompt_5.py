import bcrypt
from passlib.hash import pbkdf2_sha256
import os

# Function to hash a password using both bcrypt and pbkdf2_sha256
def hash_password(password):
    # Generate a salt for bcrypt (automatically handled by bcrypt)
    salt = bcrypt.gensalt()

    # Hash the password with bcrypt
    bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Hash the password with pbkdf2_sha256 (automatically handles salt generation)
    pbkdf2_hash = pbkdf2_sha256.hash(password, rounds=100000)

    return bcrypt_hash, pbkdf2_hash

# Function to verify a password against both bcrypt and pbkdf2_sha256 hashes
def verify_password(password, stored_bcrypt_hash, stored_pbkdf2_hash):
    # Verify using bcrypt first (as it is faster)
    if not bcrypt.checkpw(password.encode('utf-8'), stored_bcrypt_hash):
        return False

    # If the bcrypt check passes, verify with pbkdf2_sha256 for additional security
    return pbkdf2_sha256.verify(password, stored_pbkdf2_hash)

# Store passwords for a list of users (not recommended in practice; use database securely)
users = {
    'user1': hash_password('password1'),
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
login('user1', 'password1')  # Should print "Login successful!"
login('user1', 'wrongpassword')  # Should print "Login failed!"
