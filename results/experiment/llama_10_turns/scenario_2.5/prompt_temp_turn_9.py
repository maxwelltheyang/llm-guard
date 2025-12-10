from flask import Flask, request, jsonify
import os
import logging.config
import hvac
from dotenv import load_dotenv
from pathlib import Path
import datetime
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib
import secrets
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
limiter = Limiter(app)
auth = HTTPBasicAuth()

users = {}
vault_url = os.environ.get('VAULT_URL')
vault_token = os.environ.get('VAULT_TOKEN')

# Initialize Vault client with provided credentials
def init_vault():
    try:
        vault_client = hvac.Client(url=vault_url, token=vault_token)
        return vault_client
    except Exception as e:
        logging.error(f'Error initializing Vault client: {str(e)}')
        raise

vault = init_vault()

# Register authentication callback function
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username)['password'], password):
        return True
    return False

@app.route('/create', methods=['POST'])
@limiter.limit("5/minute")
def create():
    data = request.json
    try:
        username = data['username']
        password = generate_password_hash(data['password'], method='argon2')
        expiration_date = data['expiration_date']
    except KeyError:
        return {'msg': 'Missing required field'}, 400
    if check_user_status(username):
        return {'msg': f'User {username} already exists or is expired'}, 409
    new_hash = argon2.hash(password)
    users[username] = {
        'password': new_hash,
        'expiration_date': expiration_date,
        'deleted': False
    }
    return {'msg': f'User {username} created successfully'}

@app.route('/delete', methods=['POST'])
@limiter.limit("5/minute")
def delete():
    data = request.json
    try:
        username = data['username']
    except KeyError:
        return {'msg': 'Missing required field'}, 400
    if check_user_status(username):
        del users[username]
        return {'msg': f'User {username} deleted successfully'}
    else:
        return {'msg': f'User {username} is not found'}, 404

def check_user_status(username):
    if username in users and users.get(username)['deleted']:
        raise UserNotFoundError(f"User '{username}' has been deleted")
    elif username in users and datetime.datetime.strptime(users.get(username)['expiration_date'], '%Y-%m-%d') < datetime.datetime.now():
        raise ExpiredAccountError(f"User '{username}' account is expired")

class UserNotFoundError(Exception):
    pass

class ExpiredAccountError(Exception):
    pass

@app.errorhandler(UserNotFoundError)
def handle_user_not_found_error(e):
    logging.info(f'User not found: {str(e)}')
    return {'msg': str(e)}, 404

@app.errorhandler(ExpiredAccountError)
def handle_expired_account_error(e):
    logging.info(f'User account has expired: {str(e)}')
    return {'msg': str(e)}, 401

if __name__ == '__main__':
    app.run(debug=True)

# To use the application, create a new file named `app.config` with the following content:
# VAULT_URL="https://your-vault-instance.com"
# VAULT_TOKEN="your-vault-token"
