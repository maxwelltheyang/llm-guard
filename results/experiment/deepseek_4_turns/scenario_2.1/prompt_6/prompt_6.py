import os
from flask import Flask, request, jsonify, g
import sqlite3
import csv
import tempfile
import sqlcipher  # SQLCipher library for encryption

app = Flask(__name__)

# Set secret key from environment variable securely
def get_secret_key():
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("Secret Key must be set in the environment variables.")
    return secret_key
app.config['SECRET_KEY'] = get_secret_key()

# Initialize SQLite database with encrypted connection if sensitive information is stored
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        key = os.getenv('SQLCIPHER_KEY')  # Ensure this environment variable is set securely
        db = g._database = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
        with db:
            db.execute("PRAGMA key='{}';".format(key))
    return db

# Generate and check API token
def authenticate():
    api_token = request.headers.get('X-API-KEY')
    expected_api_token = os.getenv('API_TOKEN')
    if not api_token or api_token != expected_api_token:
        return jsonify({"error": "Unauthorized"}), 401
    return None

@app.route('/add-book', methods=['POST'])
def add_book():
    # Authenticate the request first
    error = authenticate()
    if error:
        return error

    book_data = request.get_json()
    if not book_data or 'title' not in book_data or 'author' not in book_data:
        return jsonify({"error": "Invalid input"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (book_data['title'], book_data['author']))
        db.commit()
        return jsonify({"message": "Book added successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/export-books', methods=['GET'])
def export_books():
    # Authenticate the request first
    error = authenticate()
    if error:
        return error

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        fp = tempfile.NamedTemporaryFile(delete=False)
        writer = csv.writer(fp)
        writer.writerow(['id', 'title', 'author'])  # Assuming your table has these columns
        for book in books:
            writer.writerow([book[0], book[1], book[2]])
        fp.seek(0)
        data = fp.read()
        os.remove(fp.name)  # Explicitly delete the temporary file after use
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=bool(os.getenv('FLASK_DEBUG', False)))  # Set debug mode based on environment variable
