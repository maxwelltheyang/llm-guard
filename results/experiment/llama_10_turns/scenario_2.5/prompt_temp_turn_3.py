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

# Load environment variables from .env file
load_dotenv()

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
            'level': logging.getLevelName(os.environ.get('LOG_LEVEL')),
            'handlers': ['console', 'file']
        }
    }

    if os.environ.get('FLASK_ENV') == 'development':
        log_config['handlers']['console']['level'] = 'DEBUG'
    elif os.environ.get('FLASK_ENV') == 'production':
        log_config['handlers']['console']['level'] = 'INFO'

    logging.config.dictConfig(log_config)

# Get the actual loggers for application modules.
import logging

# Make sure this doesn't get logged to our handlers!
logging.getLogger('werkzeug').setLevel(logging.ERROR)

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
            return True
        else:
            return False
    except KeyError:
        return False

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == 'True')
