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

import bcrypt  # Import the bcrypt library for secure password hashing

def get_db_url():
    return f"{Config.DATABASE_URL}?charset=utf8mb4"

# Create database connection URL using SQLAlchemy
db_url = get_db_url()

# Initialize the database connection
engine = create_engine(db_url)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)  

# Create all tables in the database
Base.metadata.create_all(engine)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('Authorization')
        if not session_token:
            return {'message': 'Unauthorized'}, 401

        username = get_user_from_session(session_token)
        permissions = get_permissions_for_username(username)

        # Check if the file is accessible to the user
        allowed_files = [perm.filename for perm in permissions]
        if request.args.get('filename') not in allowed_files:
            return {'message': 'Forbidden'}, 403

        return f(*args, **kwargs)
    return decorated_function

def get_user_from_session(session_token):
    session = Session()
    user = session.query(User).filter_by(token=session_token).first()
    if user is None:
        raise ValueError("Invalid or expired token")
    return user.username

class TokenBlacklist(db.Model):
    id = Column(Integer, primary_key=True)
    token = Column(String(128), nullable=False)

def get_permissions_for_username(username):
    permissions_session = sessionmaker(bind=engine)()
    result = permissions_session.query(Permission).filter_by(username=username).all()
    return result

# Input validation for the /upload endpoint
def validate_file_input(file):
    if not file.filename or '.' not in file.filename:
        raise ValueError("Invalid filename")

from app_runner import run_app  # Import from your app_runner module

if __name__ == "__main__":
    with engine.connect() as conn:
        token_blacklist = TokenBlacklist()
        conn.execute(token_blacklist.__table__.insert(), [token_blacklist.token])

    run_app(app)
