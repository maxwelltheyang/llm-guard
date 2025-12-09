import os
import sqlite3
from flask import Flask, request, jsonify, g
from flask_session import Session  # Importing session management

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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create tables if they don't exist
def init_db():
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS borrowers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE)''')
        conn.commit()

init_db()

# Route to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data['title']
    author = data['author']
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        db.commit()
        return jsonify({'id': cursor.lastrowid, 'title': title, 'author': author})
    except sqlite3.Error as e:
        db.rollback()
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Failed to add book"}), 500

# Route to add a new borrower
@app.route('/borrowers', methods=['POST'])
def add_borrower():
    data = request.get_json()
    name = data['name']
    email = data['email']
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO borrowers (name, email) VALUES (?, ?)", (name, email))
        db.commit()
        return jsonify({'id': cursor.lastrowid, 'name': name, 'email': email})
    except sqlite3.Error as e:
        db.rollback()
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Failed to add borrower"}), 500

if __name__ == '__main__':
    # Use Flask's built-in server in production mode with debug set to False
    app.run(debug=False)
