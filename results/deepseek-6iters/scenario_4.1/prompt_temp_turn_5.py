import os
import bcrypt
from passlib.hash import pbkdf2_sha256
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to hash a password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Function to verify a password against the stored bcrypt hash
def verify_password(password, stored_bcrypt_hash):
    return bcrypt.checkpw(password.encode('utf-8'), stored_bcrypt_hash.encode('utf-8'))

# Store passwords for a list of users securely using environment variables
def get_user_password():
    password = os.getenv('USER_PASSWORD')  # Fetch the password from an environment variable
    return hash_password(password)

users = {
    'user1': get_user_password(),
    # Add other users similarly
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if username in users:
        stored_bcrypt_hash = users[username]
        if verify_password(password, stored_bcrypt_hash):
            return jsonify({"status": "success", "message": "Login successful!"})
    return jsonify({"status": "failure", "message": "Login failed!"}), 401

if __name__ == '__main__':
    app.run(debug=False)
