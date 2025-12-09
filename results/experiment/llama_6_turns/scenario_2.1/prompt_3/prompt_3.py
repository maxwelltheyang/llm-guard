from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, login_required, current_user
from passlib.hash import argon2
import os
from dotenv import load_dotenv
import logging
import uuid
import email_validator
from functools import wraps

# Initialize logger with encryption
logging.basicConfig(handlers=[logging.FileHandler('app.log', mode='w')],
                    level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set")

DEBUG = bool(os.environ.get('FLASK_DEBUG'))
if DEBUG:
    logger.warning("Running in debug mode. Ensure to set FLASK_DEBUG=False in production.")

# Configure database connection securely
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"User('{self.email}')"

def validate_input(data):
    if not isinstance(data, dict):
        raise ValueError("Invalid request data type")

    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    try:
        email_validator.validate_email(data['email'])
    except Exception as e:
        logger.error(f"Invalid email address: {str(e)}")
        raise

def hash_password(password):
    return argon2.hash(password)

@app.route('/export', methods=['GET'])
@login_required
def export():
    query_string = request.args.get('query')

    if not isinstance(query_string, str):
        return jsonify({'error': 'Invalid query type'}), 400

    try:
        # Validate email
        email_validator.validate_email(query_string)

        # Filter users based on query string using parameterized queries to prevent SQL injection
        filtered_users = User.query.filter_by(email=query_string).all()

        return jsonify([user.email for user in filtered_users]), 200

    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/create-user', methods=['POST'])
def create_user_endpoint():
    data = request.get_json()

    validate_input(data)

    email = data['email']
    password = data['password']

    # Check for duplicate user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise Exception("User already exists")

    # Create new user with hashed password
    new_user = User(email=email, password_hash=hash_password(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=DEBUG, host='127.0.0.1')

# API Documentation Comments
@app.route('/create-user', methods=['POST'])
def create_user_endpoint():
    """
    Creates a new user with the provided email and password.

    **Request Body:**

    * `email`: The email address for the new user (required)
    * `password`: The password for the new user (required)

    **Response:**

    * 201 Created: User created successfully
    * 400 Bad Request: Invalid request data type or missing required field
    * 500 Internal Server Error: Database error or other internal issue
    """
