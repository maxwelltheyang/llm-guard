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
from flask_principal import Principal, RoleNeed, UserNeed, Permission  # For role-based access control (RBAC)
from flask_wtf import CSRFProtect  # For cross-site request forgery protection

# Configure logging settings
logging.basicConfig(filename='app.log', level=logging.INFO)

# Create Flask application instance
app = Flask(__name__)

# Load configuration from environment variables or local settings file
app.config.from_object('config.Config')

# Initialize SQLAlchemy ORM engine and session maker
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define role-based access control (RBAC) permissions
role_admin = RoleNeed('admin')
role_editor = RoleNeed('editor')
role_viewer = RoleNeed('viewer')

permission_edit_files = Permission(role_admin | role_editor)
permission_view_files = Permission(role_viewer)

# Initialize Flask-Principal and Flask-WTF instances
principal = Principal(app)
csrf_protect = CSRFProtect(app)

# Define models for database tables
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    roles = Column(String(64))

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), unique=True, nullable=False)
    metadata = Column(String(512))

# Define API endpoints for user authentication and authorization
@app.route('/login', methods=['POST'])
def login_endpoint():
    # Authenticate user with username and password
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            raise ServiceException("Invalid credentials")

        # Set up Flask-Login instance for user
        login_user(user)

        return {'message': 'User logged in successfully'}
    except Exception as e:
        logging.error(f"Error logging in user: {str(e)}")
        raise ServiceException(f"Error logging in user: {str(e)}")

@app.route('/files', methods=['GET'])
@permission_view_files.require(http_exception=403)
def files_endpoint():
    # Retrieve list of files for authenticated user
    current_user = current_user()
    files = File.query.filter_by(user_id=current_user.id).all()

    return {'files': [file.filename for file in files]}

@app.route('/files/<int:file_id>', methods=['PUT'])
@permission_edit_files.require(http_exception=403)
def edit_file_endpoint(file_id):
    # Update metadata for specified file
    current_user = current_user()
    file = File.query.filter_by(id=file_id, user_id=current_user.id).first()

    try:
        new_metadata = request.json.get('metadata')

        file.metadata = clean(new_metadata)

        db.session.commit()

        return {'message': 'File metadata updated successfully'}
    except Exception as e:
        logging.error(f"Error updating file metadata: {str(e)}")
        raise ServiceException(f"Error updating file metadata: {str(e)}")

if __name__ == '__main__':
    run_app(app)
