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
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')  # Use environment variable for secret key
jwt = JWTManager(app)

# Load environment variables
env_variables: Dict[str, str] = {
    'DB_HOST': os.environ.get('DB_HOST', 'localhost'),
    'DB_PORT': os.environ.get('DB_PORT', '5432'),
    'DB_USERNAME': os.environ.get('DB_USERNAME'),  # Use environment variable for sensitive data
    'DB_PASSWORD': os.environ.get('DB_PASSWORD')  # Use environment variable for sensitive data
}

# External configuration file for database connection details
config = {
    'database_path': os.environ.get('DATABASE_FILE'),
    'db_username': env_variables['DB_USERNAME'],
    'db_password': env_variables['DB_PASSWORD']
}

# Function to add book with robust error handling and input validation
def add_book() -> tuple:
    try:
        title = request.json.get('title')

        # Validate user input and sanitize query parameters
        if not isinstance(title, str) or len(title) > 255:
            return jsonify(error="Invalid title"), 400

        with sqlite3.connect(config['database_path']) as db:
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
        logger.error(f"Unexpected error adding book: {str(e)}")
        return jsonify(error=str(e)), 500

# API endpoint for adding a new book
@app.route('/books', methods=['POST'])
@jwt_required()
def api_add_book():
    return add_book()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')

    app.run(host=host, port=port)
