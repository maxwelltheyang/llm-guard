from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to SQLite database. It will be created if it doesn't exist.
conn = sqlite3.connect('library.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS books
             (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS borrowers
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS borrowed_books
             (id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER, borrower_id INTEGER,
              FOREIGN KEY(book_id) REFERENCES books(id),
              FOREIGN KEY(borrower_id) REFERENCES borrowers(id))''')

# Insert some data for testing
c.execute("INSERT INTO books (title, author) VALUES ('Book 1', 'Author 1')")
c.execute("INSERT INTO books (title, author) VALUES ('Book 2', 'Author 2')")

c.execute("INSERT INTO borrowers (name, email) VALUES ('Borrower 1', 'borrower1@example.com')")
c.execute("INSERT INTO borrowers (name, email) VALUES ('Borrower 2', 'borrower2@example.com')")

conn.commit()

# API Endpoints
@app.route('/books', methods=['GET'])
def get_books():
    c.execute('SELECT * FROM books')
    return jsonify({'books': [{'id': row[0], 'title': row[1], 'author': row[2]} for row in c.fetchall()]})

@app.route('/borrowers', methods=['GET'])
def get_borrowers():
    c.execute('SELECT * FROM borrowers')
    return jsonify({'borrowers': [{'id': row[0], 'name': row[1], 'email': row[2]} for row in c.fetchall()]])

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    c.execute('SELECT * FROM books WHERE id=?', (book_id,))
    return jsonify({'book': {'id': book_id, 'title': c.fetchone()[1], 'author': c.fetchone()[2]}})

@app.route('/borrowers/<int:borrower_id>', methods=['GET'])
def get_borrower(borrower_id):
    c.execute('SELECT * FROM borrowers WHERE id=?', (borrower_id,))
    return jsonify({'borrower': {'id': borrower_id, 'name': c.fetchone()[1], 'email': c.fetchone()[2]}})

@app.route('/books/<int:book_id>/borrowed', methods=['GET'])
def get_borrowed_book(book_id):
    c.execute('SELECT * FROM borrowed_books WHERE book_id=?', (book_id,))
    borrowed = c.fetchall()
    return jsonify({'borrowed': [{'id': row[0], 'borrower_id': row[1]} for row in borrowed]})

@app.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    borrower_id = request.json['borrower_id']
    c.execute('INSERT INTO borrowed_books (book_id, borrower_id) VALUES (?, ?)', (book_id, borrower_id))
    conn.commit()
    return jsonify({'message': 'Book borrowed successfully'})

@app.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    c.execute('DELETE FROM borrowed_books WHERE book_id=? AND borrower_id=?', (book_id, request.json['borrower_id']))
    conn.commit()
    return jsonify({'message': 'Book returned successfully'})

if __name__ == '__main__':
    app.run(debug=True)
