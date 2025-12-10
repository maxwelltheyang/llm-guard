import sqlite3
from flask import Flask, jsonify, request
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
import re
import string

app = Flask(__name__)

# Load environment variables for the application
if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    raise Exception("No database configuration found")

if 'JWT_SECRET_KEY' in os.environ:
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
else:
    raise Exception("No JWT secret key found")


# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Initialize the CSRF protection middleware
CSRFProtect(app)

# Initialize the JWT manager for token-based authentication
jwt = JWTManager(app)


def validate_password(password):
    """
    Validate a password based on complexity rules.

    Args:
        password (str): The password to be validated

    Returns:
        bool: True if the password is valid, False otherwise
    """
    if len(password) < 8:
        logger.warning("Password is too short")
        return False

    # Check for at least one digit
    if not re.search(r"\d", password):
        logger.warning("Password should have at least one digit")
        return False

    # Check for at least one lowercase letter
    if not re.search(r"[a-z]", password):
        logger.warning("Password should have at least one lowercase letter")
        return False

    # Check for at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        logger.warning("Password should have at least one uppercase letter")
        return False

    # Check for at least one special character
    if not re.search(r"[^A-Za-z0-9]", password):
        logger.warning("Password should have at least one special character")
        return False

    return True


@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user in the application.

    Args:
        username (str): The username of the user
        email (str): The email address of the user
        password (str): The password for the user

    Returns:
        A JSON response with a success message and the user's details
    """
    data = request.json
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']
    email = data['email']
    password = data['password']

    # Validate the input data
    if not validate_username(username):
        return jsonify({'error': 'Invalid username'}), 400
    if not validate_email(email):
        return jsonify({'error': 'Invalid email address'}), 400

    try:
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({'error': 'Username already exists'}), 400

        new_user = User(username, email, generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        access_token = jwt.create_access_token(identity=new_user.id)
        return jsonify(access_token=access_token), 200
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Failed to create user'}), 500


def validate_username(username):
    """
    Validate a username based on the application's rules.

    Args:
        username (str): The username to be validated

    Returns:
        bool: True if the username is valid, False otherwise
    """
    if len(username) < 3 or len(username) > 32:
        return False
    if not re.search(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True


def validate_email(email):
    """
    Validate an email address based on the application's rules.

    Args:
        email (str): The email address to be validated

    Returns:
        bool: True if the email is valid, False otherwise
    """
    if len(email) < 5 or len(email) > 254:
        return False
    if not re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    return True


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)

if __name__ == '__main__':
    if app.config['DEBUG']:
        db.create_all()
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)
    else:
        # Use WSGI server to disable debug toolbar in production
        from waitress import serve
        host = '127.0.0.1'
        port = 5000
        serve(app, host=host, port=port)
