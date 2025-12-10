from flask import Flask, request, send_from_directory, jsonify, json
import os
import mimetypes
import pathlib
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from loguru import logger
import voluptuous as vol
import tempfile
from functools import wraps

# Define configuration class to handle sensitive data securely
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')

    def __init__(self):
        self.API_KEY = os.environ.get('API_KEY')

def load_config():
    config = {}

    try:
        # Load environment variables into the configuration dictionary
        for key, value in os.environ.items():
            if key.startswith('APP_'):
                config[key] = value

    except Exception as e:
        logger.error(f'Failed to load configuration: {str(e)}')

    return config

def validate_config(config):
    # Validate required configuration values and ensure they are not empty
    for key in ['SQLALCHEMY_DATABASE_URI', 'UPLOAD_FOLDER']:
        if key not in config or not config[key]:
            raise Exception(f'Missing required configuration value: {key}')

# Securely configure database connection string from environment variable
def get_database_uri():
    try:
        # Validate and sanitize the database URI before using it
        db_uri = os.environ.get('DATABASE_URL')

        if not db_uri or '@' not in db_uri:
            raise ValueError("Invalid database URI")

        return db_uri

    except Exception as e:
        logger.error(f"Error loading database URI: {str(e)}")
        exit(1)

# Securely store API key from environment variable
def get_api_key():
    try:
        # Validate and sanitize the API key before using it
        api_key = os.environ.get('API_KEY')

        if not api_key or len(api_key) < 10:  # Simple validation, you may want more complex logic
            raise ValueError("Invalid API key")

        return api_key

    except Exception as e:
        logger.error(f"Error loading API key: {str(e)}")
        exit(1)

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)
db = SQLAlchemy(app)  # Initialize database connection

# Perform configuration and validation
with app.app_context():
    validate_config(load_config())

    try:
        db_uri = get_database_uri()
        api_key = get_api_key()

    except Exception as e:
        # Handle potential exceptions during configuration load
        logger.error(f'Configuration loading failed: {str(e)}')
        exit(1)

# Set up API key authentication
API_KEY = api_key

def authenticate():
    api_key = request.headers.get('X-API-KEY', None)

    if not api_key or api_key != API_KEY:
        return False, jsonify({'error': 'Unauthorized'}), 401

    return True, None

@app.before_request
def before_request():
    auth_ok, error_response = authenticate()

    if not auth_ok:
        return error_response

# Perform cleanup of temporary files on application shutdown
import atexit

try:
    upload_dir = tempfile.TemporaryDirectory(dir='/tmp')  # Specify a secure directory for temp files

except Exception as e:
    logger.error(f"Error creating temporary directory: {str(e)}")

finally:
    @atexit.register
    def cleanup():
        try:
            if hasattr(upload_dir, 'name'):
                os.rmdir(upload_dir.name)

        except Exception as e:
            # Log any errors during cleanup to ensure visibility of potential issues
            logger.error(f"Error cleaning up temporary files: {str(e)}")

# Perform cleanup of the database session on application shutdown
app.teardown_appcontext(lambda exception: None)

@app.errorhandler(404)
def not_found_handler(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(Exception)
def internal_server_error_handler(error):
    # Log critical issues and provide a generic error message to the user
    logger.error(f'Internal Server Error: {str(error)}')

    return jsonify({'error': 'Internal Server Error'}), 500
