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

users = {}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return users[username]['hashed_password'] == hashlib.pbkdf2_hmac('sha256', password.encode(), hashlib.sha256(secrets.token_bytes(60)).digest(), 100000)
    return False

limiter = Limiter(
    app,
    key_func=get_remote_address
)
limiter.limit("10/minute")(app.route('/'))

@auth.login_required
@limiter.limit("10/minute")
@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

# Generate encryption key securely using a secrets management service
vault_url = os.environ.get('VAULT_URL')
vault_token = os.environ.get('VAULT_TOKEN')

if not vault_url or not vault_token:
    print("Error: Vault URL and/or Token are not set")
else:
    try:
        # Use the Vault API to retrieve the encryption key securely
        import hvac
        client = hvac.Client(url=vault_url, token=vault_token)
        encryption_key_response = client.read_secrets('secret/encryption-key')
        if 'data' in encryption_key_response and 'key' in encryption_key_response['data']:
            print("Loaded Encryption Key: ", encryption_key_response['data']['key'])
        else:
            print("Error: Unable to retrieve encryption key from Vault")
    except Exception as e:
        logging.error(f"Failed to load existing encryption key: {str(e)}")

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == 'True')
