import os
from flask import Flask, request, jsonify, g
import sqlite3

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

# Endpoint to search books by title or author
@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        # Search for books by title or author
        cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", ('%' + query + '%', '%' + query + '%'))
        results = cursor.fetchall()
        books = [{'id': row[0], 'title': row[1], 'author': row[2]} for row in results]
        return jsonify(books)
    except sqlite3.Error as e:
        db.rollback()
        app.logger.error(f"Database error: {e}")
        return jsonify({"error": "Failed to search books"}), 500

if __name__ == '__main__':
    # Use Flask's built-in server in production mode with debug set to False
    app.run(debug=False)
