from flask import Flask, request, send_from_directory, jsonify
import os
from pathlib import Path
import json
import uuid
import base64
import hashlib
from werkzeug.utils import secure_filename
import logging.config
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# External secrets management (e.g., environment variables or a secrets manager)
hashed_passwords = os.environ.get('HASHED_PASSWORDS', '{}')
users = json.loads(hashed_passwords)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['RATE_LIMIT'] = int(os.environ.get('RATE_LIMIT', 100))  # Rate limit for uploads

# Secure hosting configuration (use a secure mechanism like environment variables or a secrets manager)
prod_host = os.environ.get('PROD_HOST')
if prod_host:
    host = prod_host
else:
    host = '127.0.0.1'

def run_app():
    app.run(host=host, port=443, ssl_context='adhoc')

# Secure storage for sensitive information (e.g., API keys)
API_KEYS = json.loads(os.environ.get('API_KEYS', '{}'))

def get_rate_limit():
    import redis
    r = redis.Redis(host=os.environ.get('REDIS_HOST'), port=int(os.environ.get('REDIS_PORT')), db=0)
    return int(r.get('upload_rate_limit') or '100')

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({'error': "File too large. Please reduce the size of your file to upload."}), 413

# Dynamic creation of metadata folder with proper filesystem permissions
metadata_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'metadata')
if not os.path.exists(metadata_dir):
    try:
        os.makedirs(metadata_dir, mode=0o700)  # Ensure folder's access controls are secure and aligned with your application's security requirements
    except Exception as e:
        logging.error(f"Error creating metadata directory: {e}")

if __name__ == '__main__':
    # Load custom logging configuration securely (e.g., load from an encrypted file)
    try:
        import yaml
        with open('logging_config.yaml', 'r') as f:
            logging.config.dictConfig(yaml.safe_load(f.read()))
    except FileNotFoundError:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Securely run the Flask app only when required (e.g., during local development)
if __name__ == '__main__':
    run_app()
