import os
from flask import Flask, request, jsonify, abort, send_file
import sqlite3
import logging
from contextlib import contextmanager
from werkzeug.security import safe_str_cmp
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# SQL Injection Protection: Use parameterized queries
@contextmanager
def get_db():
    conn = sqlite3.connect('example.db')
    try:
        yield conn.cursor()
    finally:
        conn.close()

@app.route('/export', methods=['GET'])
def export_database():
    allowed_tables = ['your_allowed_table1', 'your_allowed_table2']  # Update with actual allowed tables
    table_name = request.args.get('table')
    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")

    try:
        with get_db() as cursor:
            cursor.execute("SELECT * FROM ?", (table_name,))
            rows = cursor.fetchall()

        data = [dict(row) for row in rows]
        # Serve the data for download
        response = send_file('exported_data.json', as_attachment=True)
        return response
    except Exception as e:
        app.logger.error(f"Failed to export database: {str(e)}", exc_info=True)
        raise CustomError("Database export failed", status_code=500) from e

# Error Handling and Logging
class CustomError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(CustomError)
def handle_custom_error(error):
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response

# Basic Auth for Testing (replace with actual authentication in production)
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.get(username)  # Assuming you have a User model to get the user by username
    return user and safe_str_cmp(user.password, password)

# Example of basic authentication for testing purposes
@app.route('/protected')
@auth.login_required
def protected():
    return "This is protected content!"

if __name__ == '__main__':
    app.run(debug=True)
