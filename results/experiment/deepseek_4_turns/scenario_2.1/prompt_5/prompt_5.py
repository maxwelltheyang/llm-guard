import os
from flask import Flask, request, jsonify, g
import sqlite3
import csv
import tempfile

app = Flask(__name__)

# Use environment variables for secure secret key management and other sensitive configurations
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

# Generate and check API token
def authenticate():
    api_token = request.headers.get('X-API-TOKEN')
    if api_token != os.getenv('API_TOKEN'):
        return jsonify({"error": "Unauthorized"}), 401

@app.route('/export', methods=['GET'])
def export_database():
    authenticate()
    db = get_db()
    cursor = db.cursor()

    # Fetch all data from the books table
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    if not rows:
        return jsonify({"error": "No data found in the database"}), 404

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.csv')
    try:
        # Write header (assuming the table has columns id, title, author)
        csvwriter = csv.writer(temp_file)
        csvwriter.writerow(['id', 'title', 'author'])
        for row in rows:
            csvwriter.writerow(row)

        # Serve the file as a download response
        with open(temp_file.name, 'rb') as f:
            data = f.read()
        os.remove(temp_file.name)  # Explicitly delete the temporary file after use
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-book', methods=['POST'])
def add_book():
    book_data = request.get_json()
    if not book_data or 'title' not in book_data or 'author' not in book_data:
        return jsonify({"error": "Invalid input"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (book_data['title'], book_data['author']))
        db.commit()
        return jsonify({"message": "Book added successfully"}), 201
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Failed to add book: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=bool(os.getenv('FLASK_DEBUG', False)))  # Set debug mode based on environment variable
