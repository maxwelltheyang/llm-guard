from flask import Flask, request, send_file
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort
import logging
import json
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import ssl
from bleach import clean

# Import necessary libraries
import secrets  # For generating secure tokens
import sqlite3  # For database operations
from flask_sqlalchemy import SQLAlchemy  # Import the Flask-SQLAlchemy library
from flask_login import LoginManager, UserMixin  # For user authentication and authorization

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Configure the database connection URI
db = SQLAlchemy(app)  # Initialize the database object

# Define a Unified Exception class to handle different types of exceptions uniformly
class ServiceException(Exception):
    def __init__(self, message, status_code=None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        else:
            self.status_code = 500  # Default status code for internal server error

# Define a User model using SQLAlchemy
class User(db.Model, UserMixin):
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
    metadata = Column(String(512))  # Store JSON metadata as string

    def __init__(self, user_id, filename, metadata=None):
        self.user_id = user_id
        self.filename = filename
        if metadata is not None:
            self.metadata = json.dumps(metadata)

# Define a function to get the list of filenames for a given user
@app.route('/filenames', methods=['GET'])
def get_filenames_endpoint():
    token = request.args.get('token')

    try:
        # Authenticate the user
        current_user = User.query.filter_by(token=token).first()
        if not current_user:
            raise ServiceException("Invalid token", status_code=401)

        # Get the list of filenames for the current user
        filenames = [clean(file.filename) for file in File.query.filter_by(user_id=current_user.id).all()]

        return {'filenames': filenames}
    except Exception as e:
        raise ServiceException(f"Error retrieving filenames: {str(e)}")

# Define a function to upload files and metadata
@app.route('/upload', methods=['POST'])
def upload_files_endpoint():
    token = request.args.get('token')

    try:
        # Authenticate the user
        current_user = User.query.filter_by(token=token).first()
        if not current_user:
            raise ServiceException("Invalid token", status_code=401)

        # Get file metadata from request
        metadata = json.loads(request.json.get('metadata'))

        # Save file and metadata to database
        filename = request.files['file'].filename
        new_file = File(current_user.id, filename, metadata)
        db.session.add(new_file)
        db.session.commit()

        return {'message': 'File uploaded successfully'}
    except Exception as e:
        raise ServiceException(f"Error uploading file: {str(e)}")

if __name__ == '__main__':
    run_app(app)
