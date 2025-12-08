import os
from flask import Flask, request, jsonify, abort
import sqlite3

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

# Enhanced Error Handling to avoid revealing sensitive information
class CustomError(Exception):
    def __init__(self, message="An internal server error occurred", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

@app.errorhandler(CustomError)
def handle_custom_error(error):
    response = {'error': 'An error occurred, please try again later.'}
    return jsonify(response), error.status_code

# Log Management with more detailed logging
import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# SSL Configuration for HTTPS
if not app.debug:
    from flask_sslify import SSLify
    sslify = SSLify(app)

# Remove Debug Mode in Production
if __name__ == '__main__':
    app.run(debug=False)  # Set debug=False if running in production
