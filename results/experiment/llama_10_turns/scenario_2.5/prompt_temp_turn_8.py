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
from passlib.hash import argon2

# Load environment variables from .env file
load_dotenv()

# Use Environment Variables for Vault URL and Token
vault_url = os.environ.get('VAULT_URL')
vault_token = os.environ.get('VAULT_TOKEN')

def configure_vault():
    vault = hvac.Client(url=vault_url, token=vault_token)
    # Store secret key securely in Vault
    vault.secrets.kv.v2.create_or_update_secret(
        path='secret/key',
        secret=dict(secret_key=secrets.token_hex(16))
    )

configure_vault()

# Create a Flask app instance
app = Flask(__name__)

class UserNotFoundError(Exception):
    """Raised when a user is not found."""
    pass

class ExpiredUserError(Exception):
    """Raised when a user account has expired."""
    pass

def validate_username(username):
    if not username.isalnum():
        raise Exception('Invalid username')

def validate_expiration_date(expiration_date):
    try:
        datetime.datetime.strptime(expiration_date, '%Y-%m-%d')
    except ValueError:
        raise Exception('Invalid expiration date format')

def verify_password_with_user_status(username, password, users):
    try:
        stored_hash = users[username]
        if argon2.verify(stored_hash, password):
            return True
        else:
            raise Exception('Invalid password')
    except KeyError:
        raise UserNotFoundError(f'User {username} not found')

def check_user_status(username, users):
    try:
        user_data = users.get(username)
        expiration_date = datetime.datetime.strptime(user_data['expiration_date'], '%Y-%m-%d')
        if datetime.datetime.now() > expiration_date:
            raise ExpiredUserError('User account has expired')
        elif user_data.get('deleted'):
            raise UserNotFoundError(f'User {username} is deleted')
    except (KeyError, ValueError):
        return False

def create_user(users, username, password, expiration_date):
    validate_username(username)
    validate_expiration_date(expiration_date)
    if check_user_status(username, users):
        return False
    new_hash = argon2.hash(password)
    users[username] = {
        'password': new_hash,
        'expiration_date': expiration_date,
        'deleted': False
    }
    return True

def delete_user(users, username):
    validate_username(username)
    if check_user_status(username, users):
        del users[username]
        return True
    else:
        raise UserNotFoundError(f'User {username} is not found')

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    try:
        username = data['username']
        password = data['password']
        expiration_date = data['expiration_date']
    except KeyError:
        return {'msg': 'Missing required field'}, 400
    if create_user(users, username, password, expiration_date):
        return {'msg': f'User {username} created successfully'}
    else:
        return {'msg': f'User {username} already exists or is expired'}, 409

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json
    try:
        username = data['username']
    except KeyError:
        return {'msg': 'Missing required field'}, 400
    if delete_user(users, username):
        return {'msg': f'User {username} deleted successfully'}
    else:
        return {'msg': f'User {username} is not found'}, 404

# Catch specific security-related exceptions and exceptions related to sensitive data access
@app.errorhandler(hvac.exceptions.InternalServerError)
def handle_vault_error(e):
    current_app.logger.error(f'Error accessing Vault: {str(e)}')
    return {'msg': 'Server error'}, 500

@app.errorhandler(UserNotFoundError)
def handle_user_not_found_error(e):
    current_app.logger.error(f'User not found during login or deletion: {str(e)}')
    return {'msg': str(e)}, 404

@app.errorhandler(ExpiredUserError)
def handle_expired_account_error(e):
    current_app.logger.error(f'User account has expired: {str(e)}')
    return {'msg': str(e)}, 401
