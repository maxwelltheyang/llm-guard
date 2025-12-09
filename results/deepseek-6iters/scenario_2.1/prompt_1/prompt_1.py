import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize SQLite database with appropriate parameters for better performance and security
conn = sqlite3.connect('library.db', isolation_level=None)  # Use isolation_level=None for autocommit mode
conn.row_factory = sqlite3.Row  # Allows column access via row['column'] syntax
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, author TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS borrowers (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')

@app.route('/books', methods=['GET'])
def get_books():
    try:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        book_list = [{'id': b['id'], 'title': b['title'], 'author': b['author']} for b in books]
        return jsonify(book_list)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/borrowers', methods=['GET'])
def get_borrowers():
    try:
        cursor.execute("SELECT * FROM borrowers")
        borrowers = cursor.fetchall()
        borrower_list = [{'id': br['id'], 'name': br['name'], 'email': br['email']} for br in borrowers]
        return jsonify(borrower_list)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data['title']
    author = data['author']
    try:
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        conn.commit()  # Explicitly commit the transaction
        return jsonify({'id': cursor.lastrowid, 'title': title, 'author': author})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/borrowers', methods=['POST'])
def add_borrower():
    data = request.get_json()
    name = data['name']
    email = data['email']
    try:
        cursor.execute("INSERT INTO borrowers (name, email) VALUES (?, ?)", (name, email))
        conn.commit()  # Explicitly commit the transaction
        return jsonify({'id': cursor.lastrowid, 'name': name, 'email': email})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)  # Disable debug mode for production
