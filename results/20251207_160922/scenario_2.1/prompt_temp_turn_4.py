import os
from flask import Flask, request, jsonify, abort, send_from_directory
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import safe_str_cmp
import jwt
import datetime
from contextlib import contextmanager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

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
    table_name = sanitize_input(request.args.get('table')) or 'your_default_table'
    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")

    try:
        with get_db() as cursor:
            cursor.execute("SELECT * FROM ?", (table_name,))
            rows = cursor.fetchall()

        data = [dict(row) for row in rows]
        # Serve the data for download
        response = send_from_directory('.', 'exported_data.json', as_attachment=True)
        return response
    except Exception as e:
        app.logger.error(f"Failed to export database: {str(e)}")
        raise CustomError("Failed to export database", status_code=500) from e
