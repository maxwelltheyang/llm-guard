from flask import Flask, request, send_file
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort
import logging
import uuid
import json
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import ssl
from bleach import clean

# Create a new file to hold the application runner (app_runner.py)
# Move the app.run() call here for better organization and reusability.
# This will also allow us to use a more secure way of binding the Flask app.

from config import Config  # Import from your config module

# Set upload directory
UPLOAD_DIR = os.path.join(Config.UPLOAD_DIR, '')  

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = Flask(__name__)
app.config.from_object(Config)  # Load application configuration from Config class

import bcrypt  # Import necessary libraries

# Enable SSL/TLS for the app (if serving over HTTPS)
def validate_ssl_context(ssl_context):
    if not ssl_context:
        raise ValueError("SSL context is not set")

    try:
        ssl.create_default_context().load_cert_chain(*ssl_context)
    except Exception as e:
        logging.error(f"Error loading SSL context: {e}")
        raise

validate_ssl_context(app.config.get('SSL_CONTEXT'))

def validate_user_id(token):
    try:
        user_id = int(token)
        if user_id <= 0:
            raise ValueError
        return user_id
    except (ValueError, TypeError):
        logging.warning("Invalid token")
        return None

from app_runner import run_app  # Import from your app_runner module

@app.route('/list', methods=['GET'])
def get_filenames():
    try:
        token = request.cookies.get('token')  
        if not token or any(char in token for char in '<>:\\"\''):
            return {'error': 'Invalid request'}, 400

        user_id = validate_user_id(token)
        if user_id is None:
            logging.warning("Invalid token")
            return {'error': 'Invalid request'}, 400

        try:
            user = session.query(User).filter_by(id=user_id).one()
        except Exception as e:
            logging.error(f"Error retrieving user: {str(e)}")  # Log detailed error information instead of just the exception message
            raise

        try:
            filenames = [clean(file.filename) for file in session.query(File).filter_by(user_id=user.id).all()]
        except Exception as e:
            logging.error(f"Error listing filenames: {str(e)}")  # Log detailed error information instead of just the exception message
            raise

        return {'filenames': filenames}
    except Exception as e:  
        logging.error(f"Error retrieving filenames: {str(e)}")  # Log detailed error information instead of just the exception message
        raise

run_app(app, ssl_context=app.config.get('SSL_CONTEXT'))
