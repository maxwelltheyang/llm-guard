import sqlite3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging.config
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os
import re

app = Flask(__name__)

# Load environment variables for configuration
if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
if not app.config['JWT_SECRET_KEY']:
    print("Error: JWT secret key is not set.")
    exit(1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define a function to validate email addresses
def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

# Define a function to validate usernames
def validate_username(username):
    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, username))

@app.errorhandler(404)
def not_found(e):
    return jsonify(error='Not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error='Internal server error'), 500

# Define a route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify(error='Missing required fields'), 400

    username = data['username']
    email = data['email']
    password = data['password']

    # Validate the username and email address
    if not validate_username(username):
        return jsonify(error='Invalid username'), 400
    if not validate_email(email):
        return jsonify(error='Invalid email address'), 400

    # Check for existing user with the same username or email
    if User.query.filter_by(username=username).first():
        return jsonify(error='Username already exists'), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error='Email address already exists'), 400

    # Create a new user
    try:
        new_user = User(username, email, generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=new_user.id)
        return jsonify(access_token=access_token), 200
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return jsonify(error='Failed to create user'), 500

# Define a route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if 'username' not in data or 'password' not in data:
        return jsonify(error='Missing required fields'), 400

    username = data['username']
    password = data['password']

    # Find the user with the provided username
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(error='Invalid username or password'), 401

    # Check the password using Werkzeug's check_password_hash function
    if not check_password_hash(user.password, password):
        return jsonify(error='Invalid username or password'), 401

    # Generate an access token for the user
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

if __name__ == '__main__':
    if app.config['DEBUG']:
        db.create_all()
    else:
        from waitress import serve
        host = '127.0.0.1'
        port = 5000
        serve(app, host=host, port=port)
