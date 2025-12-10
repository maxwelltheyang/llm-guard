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

# Import necessary libraries
import secrets  # For generating secure tokens
import sqlite3  # For SQLite database support (if used)

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

# Define a function to generate secure tokens
def generate_token(length=32):
    return secrets.token_urlsafe(length)

# Define a function to authenticate users
def authenticate_user(token, session):
    try:
        # Check if the token is valid and exists in the database
        user = session.query(User).filter_by(token=token).one()
        return True
    except Exception as e:
        logging.error(f"Error authenticating user: {str(e)}")
        return False

# Define a function to validate user ID
def validate_user_id(user_id, session):
    try:
        # Check if the user exists in the database using parameterized query
        result = session.execute("SELECT 1 FROM users WHERE id = :id", {'id': user_id})

        # Get the user's token
        token = session.query(User.token).filter_by(id=user_id).scalar()

        return True, token
    except Exception as e:
        logging.error(f"Error validating user ID: {str(e)}")
        raise

# Define a function to get filenames for a given user
def get_filenames(user_id, session):
    try:
        # Get the list of filenames for the current user using parameterized query
        result = session.execute("SELECT filename FROM files WHERE user_id = :user_id", {'user_id': user_id})

        return [clean(file[0]) for file in result]
    except Exception as e:
        logging.error(f"Error retrieving filenames: {str(e)}")
        raise

from flask_sqlalchemy import SQLAlchemy  # Import the Flask-SQLAlchemy library
db = SQLAlchemy(app)  # Initialize the database object

# Define a User model using SQLAlchemy
class User(db.Model):
    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True)

    def __init__(self, id, token):
        self.id = id
        self.token = token

# Define a File model using SQLAlchemy
class File(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'))
    filename = Column(String(128))

    def __init__(self, user_id, filename):
        self.user_id = user_id
        self.filename = filename

# Define a function to get the list of filenames for a given user
@app.route('/filenames', methods=['GET'])
def get_filenames_endpoint():
    token = request.args.get('token')

    try:
        # Authenticate the user
        if not authenticate_user(token, db.session):
            abort(401)

        # Validate the user ID
        is_valid, user_token = validate_user_id(token, db.session)
        if not is_valid:
            logging.warning("Invalid token")
            return {'error': 'Invalid request'}, 400

        # Get the list of filenames for the current user
        filenames = get_filenames(token, db.session)

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
