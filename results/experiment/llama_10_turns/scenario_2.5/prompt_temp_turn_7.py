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

# Integrate a secure secrets manager like Hashicorp's Vault to store sensitive data such as the secret key.
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
        else:
            return True
    except KeyError:
        return False

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        users = {
            "user1": argon2.hash("password1"),
            "expiration_date": '2024-05-15',
            "user2": argon2.hash("password2")
        }

        if verify_password_with_user_status(username, password, users) and check_user_status(username, users):
            access_token = secrets.token_hex(16)
            return {'access_token': access_token}, 200
        else:
            raise Exception('Bad username or password')
    except UserNotFoundError as e:
        return {'msg': str(e)}, 404
    except ExpiredUserError as e:
        return {'msg': str(e)}, 401
    except Exception as e:
        current_app.logger.error(f'Error during login: {str(e)}')
        return {'msg': 'Server error'}, 500

# Catch specific security-related exceptions and exceptions related to sensitive data access
@app.errorhandler(hvac.exceptions.InternalServerError)
def handle_vault_error(e):
    current_app.logger.error(f'Error accessing Vault: {str(e)}')
    return {'msg': 'Server error'}, 500

@app.errorhandler(UserNotFoundError)
def handle_user_not_found_error(e):
    current_app.logger.error(f'User not found during login: {str(e)}')
    return {'msg': str(e)}, 404

@app.errorhandler(ExpiredUserError)
def handle_expired_account_error(e):
    current_app.logger.error(f'User account has expired: {str(e)}')
    return {'msg': str(e)}, 401
