import os
from flask import Flask, request, jsonify, abort, send_from_directory
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy
import tempfile
import json

app = Flask(__name__)

# Load database connection details and API keys from environment variables with validation
def validate_environment_variable(var_name, expected_type):
    var_value = os.getenv(var_name)
    if not var_value:
        raise ValueError(f"Environment variable {var_name} is not set.")
    if not isinstance(var_value, expected_type):
        raise TypeError(f"Expected {expected_type}, but got {type(var_value)} for {var_name}.")
    return var_value

DB_NAME = validate_environment_variable('DB_NAME', str)
API_KEY = validate_environment_variable('API_KEY', str)

# Use validated environment variables in your application
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SECRET_KEY'] = API_KEY

db = SQLAlchemy(app)

# Enhanced Error Handling to avoid revealing sensitive information
class CustomError(Exception):
    def __init__(self, message="An internal server error occurred", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Remove Debug Mode in Production
if os.environ.get('FLASK_ENV') == 'production':
    app.debug = False
else:
    app.debug = True

# Logging Configuration
if not app.debug:
    file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=10)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Flask-SQLAlchemy')

# Input Validation for SQL Queries
def sanitize_input(data):
    if isinstance(data, str):
        return data.replace("'", "''")
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    else:
        return data

# /export endpoint
@app.route('/export', methods=['GET'])
def export_database():
    try:
        # Sanitize the table name input to prevent SQL injection
        table_name = sanitize_input(request.args.get('table')) or 'your_default_table'

        # Connect to the SQLite database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Prepare the data to be exported
        data = []
        for row in rows:
            data.append(dict(row))

        # Use a temporary file to store the exported data
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp_file:
            json.dump(data, tmp_file, indent=4)
            tmp_file_path = tmp_file.name

        # Serve the temporary file for download
        response = send_from_directory('.', tmp_file_path, as_attachment=True)

        # Clean up the temporary file
        os.remove(tmp_file_path)

        return response
    except Exception as e:
        raise CustomError("Failed to export database", status_code=500) from e

# SSL Configuration for HTTPS in production environment
if not app.debug:
    SSLify(app, permanent=True)

if __name__ == '__main__':
    app.run()
