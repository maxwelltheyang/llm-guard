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

# Define a function to validate user ID
def validate_user_id(token, session):
    try:
        user_id = int(token)
        if user_id <= 0:
            raise ValueError
        # Check if the user exists in the database
        user = session.query(User).filter_by(id=user_id).one()
        return user_id
    except (ValueError, TypeError):
        logging.warning("Invalid token")
        return None

# Define a function to authenticate users
def authenticate_user(token, session):
    try:
        # Check if the token is valid and exists in the database
        user = session.query(User).filter_by(token=token).one()
        return True
    except Exception as e:
        logging.error(f"Error authenticating user: {str(e)}")
        return False

from app_runner import run_app  # Import from your app_runner module

@app.route('/list', methods=['GET'])
def get_filenames():
    token = request.args.get('token')

    try:
        # Get the session object
        session = Session()

        # Authenticate the user
        if not authenticate_user(token, session):
            abort(401)

        # Validate the user ID
        user_id = validate_user_id(token, session)
        if user_id is None:
            logging.warning("Invalid token")
            return {'error': 'Invalid request'}, 400

        try:
            # Get the list of filenames for the current user
            filenames = [clean(file.filename) for file in session.query(File).filter_by(user_id=user_id).all()]
        except Exception as e:
            logging.error(f"Error retrieving filenames: {str(e)}")
            raise

        return {'filenames': filenames}
    except Exception as e:
        # Log detailed error information
        logging.error(f"Error retrieving filenames: {str(e)}")

        if isinstance(e, SQLAlchemyError):
            # Handle database errors separately
            logging.error(f"Database error: {e}")
            return {'error': 'Database error'}, 500

        # Return a generic error message
        return {'error': 'Internal server error'}, 500

run_app(app, ssl_context=app.config.get('SSL_CONTEXT'))
