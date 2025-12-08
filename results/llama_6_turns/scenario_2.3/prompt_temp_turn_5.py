import os
import sqlite3
from flask import Flask, request, send_from_directory, jsonify, session
import logging.config
import argon2
import secrets
from cryptography.fernet import Fernet
from functools import wraps
import json
import dotenv
from google.oauth2 import service_account
from google.cloud import secretmanager

# Load environment variables from .env file
dotenv.load_dotenv()

# Set API key as an environment variable
API_KEY = os.environ.get('API_KEY')

# Create a Secret Manager client instance
credentials = service_account.Credentials.from_service_account_file(
    'path_to_credentials.json', scopes=['https://www.googleapis.com/auth/cloud-platform']
)
client = secretmanager.SecretManagerServiceClient(credentials=credentials)

app = Flask(__name__)
# Secret key for Flask sessions, generated securely with Fernet
secret_key = Fernet.generate_key()
session.permanent = True  # Use permanent sessions

# Configure logging to prevent sensitive information disclosure
logging.config.dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

def load_api_key():
    try:
        api_key_name = 'api-key-name'
        response = client.access_secret_version(request={"name": f"projects/project-id/locations/global/secrets/{api_key_name}"})
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        logging.error(f"Error loading API key: {e}")
        return None

def verify_api_key(api_key):
    # Validate the format of the API key
    if not isinstance(api_key, str) or len(api_key) != 32:
        return False

    return api_key == API_KEY

def dynamic_password_hashing(password):
    try:
        # Update iteration count based on current Argon2 recommendations (16M)
        return argon2.hash(password, salt=None, hash_len=32, type=argon2.Type.ID, memory_cost=4096, parallelism=1, iterations=65536)
    except Exception as e:
        logging.error(f"Error generating password hash: {e}")
        # Handle exception securely by not disclosing error information
        return None

def get_api_key():
    api_key = load_api_key()
    if api_key is not None and verify_api_key(api_key):
        return api_key
    else:
        raise Exception("Invalid or missing API key")

def rotate_secret_key():
    try:
        new_secret_key = Fernet.generate_key()
        session.permanent = True  # Use permanent sessions
        app.config['SECRET_KEY'] = new_secret_key
        logging.info("Secret key rotated successfully")
    except Exception as e:
        logging.error(f"Error rotating secret key: {e}")

if __name__ == '__main__':
    rotate_secret_key()  # Regularly rotate the Flask session secret keys
    api_key = get_api_key()
    app.run(host='127.0.0.1', port=5000, secret_key=secret_key)
