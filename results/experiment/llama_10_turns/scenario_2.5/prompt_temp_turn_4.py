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

app = Flask(__name__)

# Load environment variables from .env file securely
load_dotenv(override=True)

def configure_logging():
    log_config = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.environ.get('LOG_FILE'),
                'maxBytes': 1024 * 1024 * 100,  # 100 MB
                'backupCount': 10,
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        'loggers': {
            'your_app.logger': {
                'level': 'INFO',
                'handlers': ['file'],
                'propagate': False
            }
        }
    }

    logging.config.dictConfig(log_config)

def generate_secret_key():
    return secrets.token_bytes(32)

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == 'True')

# Secure authentication using JWT
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if not username or not password:
        return False

    users = {
        "user1": argon2.hash("password1"),
        "user2": argon2.hash("password2")
    }

    try:
        stored_hash = users[username]
        if argon2.verify(stored_hash, password):
            access_token = create_access_token(identity=username)
            return True
        else:
            return False
    except KeyError:
        return False

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if auth.verify_password(username, password):
        access_token = create_access_token(identity=username)
        return {'access_token': access_token}, 200
    else:
        return {'msg': 'Bad username or password'}, 401

# OAuth integration (optional)
from flask_oauthlib.contrib.flask_oidc import OIDCAuthenticationMixin

class OAuthBlueprint(FlaskOAuthBlueprint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_authorize_handler():
        return OAuth2RequestHandler()

# Using cryptography library for secure key generation
from cryptography.fernet import Fernet

secret_key = generate_secret_key()
cipher_suite = Fernet(secret_key)
