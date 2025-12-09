import os
from flask import Flask, request, jsonify, g
import sqlite3
import csv
import tempfile

app = Flask(__name__)

# Set secret key from environment variable
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
    api_token = request.headers.get('X-API-KEY')
    if not api_token or api_token != os.getenv('API_TOKEN'):
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
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"error": f"Failed to add book: {str(e)}"}), 500

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
