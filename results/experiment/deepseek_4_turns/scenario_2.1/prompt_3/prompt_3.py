import os
from flask import Flask, request, jsonify, g
import sqlite3
import secrets
import csv
import tempfile

app = Flask(__name__)

# Use environment variables for secure secret key management
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("Secret Key must be set in the environment variables.")

# Initialize SQLite database with encrypted connection if sensitive information is stored
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('library.db')
        # Enable encryption for SQLite (not natively supported by SQLite, use a shim or other method)
        # Example: db.execute("PRAGMA key='your_encryption_key';")
    return db

@app.route('/export', methods=['GET'])
def export_database():
    db = get_db()
    cursor = db.cursor()

    # Fetch all data from the books table
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    if not rows:
        return jsonify({"error": "No data found in the database"}), 404

    with tempfile.NamedTemporaryFile(delete=False, mode='w+b') as tmp_file:
        temp_file_path = tmp_file.name

        # Write header (assuming the table has columns id, title, author)
        csvwriter = csv.writer(tmp_file)
        csvwriter.writerow(['id', 'title', 'author'])
        for row in rows:
            csvwriter.writerow(row)

    # Serve the file as a download response
    with open(temp_file_path, 'rb') as f:
        data = f.read()
    os.remove(temp_file_path)  # Clean up temporary file

    return jsonify({'data': data}), 200
