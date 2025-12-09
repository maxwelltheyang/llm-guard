import os
import secrets
from flask import Flask

app = Flask(__name__)

# Set environment variables for secure storage
os.environ['SECRET_ID'] = 'your_secure_secret_id'  # Replace with actual secret ID before deployment
os.environ['ADMIN_USER'] = 'admin'
os.environ['ADMIN_PASS'] = 'secure_password'

def get_secret():
    secret_id = os.getenv('SECRET_ID')
    if not secret_id:
        raise ValueError("Secret ID is not set.")
    return secret_id

def admin_credentials():
    user = os.getenv('ADMIN_USER')
    password = os.getenv('ADMIN_PASS')
    if not user or not password:
        raise ValueError("Admin credentials are not set.")
    return user, password

# Generate a cryptographic secret key
app.config['SECRET_KEY'] = secrets.token_bytes(32)

if __name__ == "__main__":
    app.run(debug=False)
