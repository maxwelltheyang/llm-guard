from flask import Flask, request, jsonify
import sqlite3
import os
import configparser

app = Flask(__name__)

# Load configuration from environment variables or a production-ready configuration file
config = configparser.ConfigParser()
config.read('config.ini')

def create_app(debug_mode):
    app.config['DEBUG'] = debug_mode

    # Create a single SQLite database connection that's reused throughout the application
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Create tables if they do not exist
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                    title text,
                    author text,
                    publication_date date
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS borrowers (
                    name text,
                    email text,
                    phone_number text
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS loans (
                    book_title text,
                    borrower_name text,
                    loan_date date,
                    return_date date
                )''')

    # Define constants for database connection parameters
    DB_NAME = 'library.db'

    def execute_query(query, params=None):
        c.execute(query, params)
        conn.commit()
        return c.fetchall()

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.route('/books', methods=['GET'])
    def get_books():
        query = "SELECT * FROM books"
        rows = execute_query(query)
        return jsonify(rows)

    @app.route('/borrowers', methods=['GET'])
    def get_borrowers():
        query = "SELECT * FROM borrowers"
        rows = execute_query(query)
        return jsonify(rows)

    @app.route('/loans', methods=['GET'])
    def get_loans():
        query = "SELECT * FROM loans"
        rows = execute_query(query)
        return jsonify(rows)

    # API endpoints for adding books, borrowers, and loans
    @app.route('/books', methods=['POST'])
    def add_book():
        data = request.get_json()
        if 'title' not in data or 'author' not in data:
            return {'error': 'Missing required field(s)'}, 400

        query = "INSERT INTO books (title, author, publication_date) VALUES (?, ?, ?)"
        execute_query(query, (data['title'], data['author'], None))
        return jsonify({'message': 'Book added successfully'}), 201

    @app.route('/borrowers', methods=['POST'])
    def add_borrower():
        data = request.get_json()
        if 'name' not in data or 'email' not in data or 'phone_number' not in data:
            return {'error': 'Missing required field(s)'}, 400

        query = "INSERT INTO borrowers (name, email, phone_number) VALUES (?, ?, ?)"
        execute_query(query, (data['name'], data['email'], data['phone_number']))
        return jsonify({'message': 'Borrower added successfully'}), 201

    @app.route('/loans', methods=['POST'])
    def add_loan():
        data = request.get_json()
        if 'book_title' not in data or 'borrower_name' not in data or 'loan_date' not in data or 'return_date' not in data:
            return {'error': 'Missing required field(s)'}, 400

        query = "INSERT INTO loans (book_title, borrower_name, loan_date, return_date) VALUES (?, ?, ?, ?)"
        execute_query(query, (data['book_title'], data['borrower_name'], data['loan_date'], data['return_date']))
        return jsonify({'message': 'Loan added successfully'}), 201

    return app

if __name__ == '__main__':
    debug_mode = config.get('app', 'debug_mode') == 'True'
    app = create_app(debug_mode)

    # Disable debug mode in production settings
    if not debug_mode:
        app.config['DEBUG'] = False

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
