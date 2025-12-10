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
    salt = Column(String(128), nullable=False)

class TokenBlacklist(db.Model):
    id = Column(Integer, primary_key=True)
    token = Column(String(128), nullable=False, unique=True)

def get_user_from_session(session_token):
    try:
        session = Session(bind=engine)  # Specify the underlying database engine
        if session.query(TokenBlacklist).filter_by(token=session_token).first():
            logging.error(f"Token has been revoked: {session_token}")  
            return None, "Invalid or expired token"
        user = session.query(User).filter_by(username=get_username_from_token(session_token)).first()
        if not user:
            logging.error(f"User not found in database: {session_token}")  
            return None, "Invalid or expired token"
        return user
    except Exception as e:  # Handle potential database errors with try-except-finally
        session.rollback()  # Rollback the current transaction
        logging.error(f"Error getting user from session: {str(e)}")  
        raise

def get_permissions_for_username(username):
    try:
        session = Session(bind=engine)  # Specify the underlying database engine
        return session.query(Permission).join(User, Permission.user_id == User.id).filter_by(username=username).all()
    except Exception as e:  # Handle potential database errors with try-except-finally
        session.rollback()  # Rollback the current transaction
        logging.error(f"Error getting permissions for username: {str(e)}")  
        return []

from app_runner import run_app  # Import from your app_runner module

def create_tables(engine):
    with engine.connect() as conn:
        Base.metadata.create_all(conn)  # Create tables once during setup

if __name__ == "__main__":
    create_tables(engine)  # Check if the tables are already present in the database
    token_blacklist = TokenBlacklist()

    run_app(app)
