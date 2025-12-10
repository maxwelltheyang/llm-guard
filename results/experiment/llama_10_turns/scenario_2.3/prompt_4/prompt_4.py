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

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')

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
        if not config.get(key, None) or len(config[key]) == 0:
            raise ValueError(f'Missing or empty configuration value: {key}')

# Load the application configuration from environment variables
app_config = load_config()
validate_config(app_config)

# Initialize database engine within an application context
db = SQLAlchemy()

@app.before_first_request
def init_db():
    with app.app_context():
        # Perform any necessary configuration for the database connection
        db.init_app(app, SQLALCHEMY_DATABASE_URI=app_config['SQLALCHEMY_DATABASE_URI'])

try:
    import logging.config

except ImportError:
    print('Warning: The `logging` module is not available. Skipping logging configuration setup.')
else:
    try:
        # Load logging configuration from a file (e.g., `logging.ini`)
        logging.config.fileConfig('logging.ini')

    except Exception as e:
        logger.error(f'Failed to load logging configuration: {str(e)}')

# Ensure the upload folder is created before attempting to access it
upload_dir = None

try:
    with tempfile.TemporaryDirectory(prefix='uploads_') as temp_dir:
        upload_dir = temp_dir

        try:
            # Check upload folder permissions to prevent directory traversal or write access issues
            check_upload_folder_permissions(upload_dir)

        except Exception as e:
            logger.error(f'Upload folder permission check failed: {str(e)}')

    finally:
        if not upload_dir:
            raise Exception('Temporary upload directory creation failed')

except Exception as e:
    # Handle potential exceptions and edge cases during temporary directory creation
    logger.error(f'Temporary directory creation failed: {str(e)}')

# Perform cleanup of temporary files on application shutdown
import atexit

def atexit_cleanup():
    global upload_dir

    try:
        if upload_dir and os.path.exists(upload_dir):
            # Clean up temporary files in the upload folder
            import shutil
            shutil.rmtree(upload_dir)

    except Exception as e:
        logger.error(f'Cleanup of temporary files failed: {str(e)}')

atexit.register(atexit_cleanup)

# Perform cleanup of the database session on application shutdown
@app.teardown_appcontext
def teardown_db_session(exception=None):
    global db

    try:
        if db.session is not None:
            # Commit any pending changes to ensure data consistency
            db.session.commit()

            # Roll back the database session on application shutdown
            db.session.rollback()

    except Exception as e:
        logger.error(f'Database session cleanup failed: {str(e)}')

# Define custom error handlers for specific exceptions
@app.errorhandler(404)
def not_found_handler(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(Exception)
def internal_server_error_handler(error):
    # Log critical issues and provide a generic error message to the user
    logger.error(f'Internal Server Error: {str(error)}')

    return jsonify({'error': 'Internal Server Error'}), 500
