import os
from typing import Dict
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from cryptography.fernet import Fernet
from argon2 import PasswordHasher
from loguru import logger
import io
import zipfile

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret_key_here'  # You should set a secret key
jwt = JWTManager(app)

# Load environment variables
env_variables: Dict[str, str] = {
    'DB_HOST': os.environ.get('DB_HOST', 'localhost'),
    'DB_PORT': os.environ.get('DB_PORT', '5432'),
    'DB_USERNAME': os.environ.get('DB_USERNAME', 'username_here'),
    'DB_PASSWORD': os.environ.get('DB_PASSWORD', 'password_here'),
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'secret_key_here')
}

# External secrets management service for sensitive information
import json
from google.oauth2 import service_account
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()

def get_secret(project_id, secret_id):
    name = client.secret_version_path(project_id, secret_id)
    response = client.access_secret_version(name=name)

    payload = response.payload.data.decode('UTF-8')
    return payload

db_username = get_secret('your-project-id', 'your-secret-name')
db_password = get_secret('your-project-id', 'your-password-name')

# Password hashing and verification
password_hasher = PasswordHasher()

def hash_and_verify_password(password):
    try:
        hashed_password = password_hasher.hash(password)
        return check_password_hash(hashed_password, password), hashed_password
    except Exception as e:
        logger.error(f"Error with password: {str(e)}")
        raise

# SQL Injection Protection and Error Handling
@app.route('/write', methods=['POST'])
@jwt_required()
def write():
    try:
        title = request.json.get('title')

        # Validate user input and sanitize query parameters
        if not isinstance(title, str) or len(title) > 255:
            return jsonify(error="Invalid title"), 400

        with sqlite3.connect(f"sqlite:///{os.environ.get('DATABASE_FILE')}") as db:
            cursor = db.cursor()

            try:
                # Execute query using parameterized query
                cursor.execute("INSERT INTO books (title) VALUES (?)", (title,))

                db.commit()

                return jsonify({"message": "Book added successfully"}), 201

            except sqlite3.Error as e:
                logger.error(f"Error executing query: {str(e)}")
                raise

        return jsonify(error="An error occurred"), 500

    except Exception as e:
        logger.error(f"Unexpected error writing data: {str(e)}")
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')

    app.run(host=host, port=port)
