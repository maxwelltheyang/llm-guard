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
        username (str): The username for the new account
        email (str): The email address for the new account
        password (str): The password for the new account

    Returns:
        str: A JSON response containing the result of the registration attempt
    """
    # Check if all required fields are present in the request
    if 'username' not in request.json or 'email' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Missing required fields'}), 400

    existing_user = User.query.filter_by(username=request.json['username']).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    new_user = User(username=request.json['username'], email=request.json['email'])
    db.session.add(new_user)
    db.session.commit()

    # Validate password before setting it
    password = request.json.get('password')
    if not validate_password(password):
        return jsonify({'error': 'Invalid password'}), 400

    new_user.password = generate_password_hash(password)

    return jsonify({'message': 'User created successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    """
    Log in to the application using a username and password.

    Args:
        username (str): The username for the account
        password (str): The password for the account

    Returns:
        str: A JSON response containing the result of the login attempt
    """
    # Check if all required fields are present in the request
    if 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(username=request.json['username']).first()
    if not user or not check_password_hash(user.password, request.json['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = jwt.create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


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
