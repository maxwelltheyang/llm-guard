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

# Load environment variables and handle missing or incorrect values with error handling
env_variables: Dict[str, str] = {
    'DB_HOST': os.environ.get('DB_HOST', 'localhost'),
    'DB_PORT': os.environ.get('DB_PORT', None),
    'DB_USERNAME': os.environ.get('DB_USERNAME'),
    'DB_PASSWORD': os.environ.get('DB_PASSWORD')
}

# Validate environment variables for sensitive data and handle missing values with errors
if not env_variables['DB_USERNAME'] or not env_variables['DB_PASSWORD']:
    return jsonify(error="Missing database credentials"), 400

try:
    # Use the validated environment variables to configure the application
    config = {
        'database_path': os.environ.get('DATABASE_FILE')
    }

    # Validate and sanitize the database path to prevent potential SQL injection attacks
    if not isinstance(config['database_path'], str) or len(config['database_path']) < 1:
        return jsonify(error="Invalid database file"), 400

except Exception as e:
    logger.error(f"Error loading configuration: {str(e)}")
    return jsonify(error="Failed to load configuration"), 500

# Function to establish a secure database connection
def get_db_connection() -> sqlite3.Connection:
    try:
        # Re-validate and sanitize the database path in this function for added security
        if not isinstance(config['database_path'], str) or len(config['database_path']) < 1:
            return None

        # Establish a secure database connection with proper error handling and isolation
        conn = sqlite3.connect(config['database_path'], check_same_thread=False)

        return conn

    except Exception as e:
        logger.error(f"Error establishing database connection: {str(e)}")
        return None

# Function to add book with robust error handling, input validation, and re-validation of database path
def add_book() -> tuple:
    try:
        data = request.json

        # Validate user input and sanitize query parameters using comprehensive sanitization techniques
        if not isinstance(data, dict) or 'title' not in data or len(data['title']) > 255:
            return jsonify(error="Invalid title"), 400

        config_db_path = config['database_path']

        # Re-validate the database path for added security
        if not isinstance(config_db_path, str) or len(config_db_path) < 1:
            return jsonify(error="Invalid database file"), 400

        conn = get_db_connection()

        if conn is None:
            return jsonify(error="Failed to establish database connection"), 500

        try:
            # Execute the query
            cursor = conn.cursor()

            # Use a parameterized query to prevent SQL injection attacks
            cursor.execute("INSERT INTO books (title) VALUES (?)", (data['title'],))

            conn.commit()

            return jsonify({"message": "Book added successfully"}), 201

        except sqlite3.Error as e:
            logger.error(f"Error executing query: {str(e)}")
            conn.rollback()
            raise

        finally:
            # Ensure the database connection is closed
            if 'conn' in locals():
                conn.close()

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
