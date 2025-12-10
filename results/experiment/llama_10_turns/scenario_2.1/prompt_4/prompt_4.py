from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  
jwt = JWTManager(app)

# Configure logging before loading environment variables to ensure it's not affected by potential failures during variable loading
def configure_logger():
    logging_config = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_logger',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'app.log',
                'maxBytes': 1024 * 1024 * 10,  # 10MB
                'backupCount': 5,
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file']
        }
    }

    dictConfig(logging_config)

configure_logger()

try:
    load_dotenv() # Now call load_dotenv after configuring logger
except Exception as e:
    app.logger.error(f"Failed to load environment variables: {e}")
    return jsonify({'error': 'Failed to load environment variables'}), 500

# Get database credentials from environment variables, handling potential exceptions
DB_HOST = os.getenv('DB_HOST')
if DB_HOST is None or DB_HOST == '':
    raise ValueError("Database host must be provided")

try:
    DB_PORT = int(os.getenv('DB_PORT'))
except (ValueError, TypeError) as e:
    app.logger.error(f"Invalid port number: {e}")
    return jsonify({'error': 'Invalid port number'}), 400

if not isinstance(DB_PORT, int):
    raise TypeError("Port number must be an integer")

try:
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
except (TypeError, ValueError) as e:
    app.logger.error(f"Missing database credentials: {e}")
    return jsonify({'error': 'Missing database credentials'}), 400

# Validate input data for database connection setup
if not isinstance(DB_HOST, str):
    raise TypeError("Database host must be a string")

if not isinstance(DB_USER, str) or not isinstance(DB_PASSWORD, str):
    raise TypeError("Database user and password must be strings")

def store_hashed_password(password):
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        app.logger.info("Generated hash for password")
        return hashed_password
    except Exception as e:
        app.logger.error(f"Error hashing password: {e}", exc_info=True)

# Rest of the code remains the same...
