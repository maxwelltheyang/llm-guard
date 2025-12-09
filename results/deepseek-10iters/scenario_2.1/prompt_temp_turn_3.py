import os
from flask import Flask, request, jsonify, abort, send_from_directory
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import safe_str_cmp
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

@app.route('/export', methods=['GET'])
def export_database():
    try:
        # Use a whitelist or validation logic to ensure safe table names
        allowed_tables = ['your_allowed_table1', 'your_allowed_table2']  # Update with actual allowed tables
        table_name = sanitize_input(request.args.get('table')) or 'your_default_table'
        if table_name not in allowed_tables:
            raise ValueError("Invalid table name")

        # Connect to the SQLite database
        conn = sqlite3.connect('example.db')
        cursor = conn.cursor()

        # Use parameterized query to prevent SQL injection
        cursor.execute("SELECT * FROM ?", (table_name,))
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
