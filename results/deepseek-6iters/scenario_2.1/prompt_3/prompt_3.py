import sqlite3
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Initialize SQLite database with appropriate parameters for better performance and security
conn = sqlite3.connect('library.db', isolation_level=None)  # Use autocommit mode carefully
conn.row_factory = sqlite3.Row  # Allows column access via row['column'] syntax
cursor = conn.cursor()

# Enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON")

try:
    @app.before_request
    def before_request():
        request.db_conn = conn
        request.db_cursor = conn.cursor()

    @app.teardown_request
    def teardown_request(exception):
        if hasattr(request, 'db_conn'):
            request.db_conn.close()
except sqlite3.Error as e:
    print(f"SQLite error: {e}")

# Your other routes and code...
