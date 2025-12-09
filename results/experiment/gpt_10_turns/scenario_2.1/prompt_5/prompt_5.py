from flask import Flask, jsonify, request, abort, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os
import csv
import uuid
from functools import wraps
import logging

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
app.config['API_TOKEN'] = os.getenv('API_TOKEN')

EXPORT_DIR = 'exports'
os.makedirs(EXPORT_DIR, exist_ok=True)

# Set directory permissions to restrict access
os.chmod(EXPORT_DIR, 0o700)

db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Database Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author
        }

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

# Authentication Decorator
def require_authentication(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        expected_token = f'Bearer {app.config["API_TOKEN"]}'
        if not token or token != expected_token:
            abort(401, description='Unauthorized: Invalid or missing API token')
        return f(*args, **kwargs)
    return decorated_function

# API Endpoints
@app.route('/books', methods=['GET'])
def list_books():
    try:
        books = Book.query.all()
        return jsonify([book.to_dict() for book in books]), 200
    except SQLAlchemyError:
        logging.error("Error fetching books", exc_info=True)
        abort(500, description="Error fetching books")

@app.route('/books', methods=['POST'])
@require_authentication
def add_book():
    try:
        data = request.json
        if not data or 'title' not in data or 'author' not in data:
            abort(400, description="Bad Request: 'title' and 'author' are required")

        new_book = Book(title=data['title'], author=data['author'])
        db.session.add(new_book)
        db.session.commit()
        return jsonify(new_book.to_dict()), 201
    except SQLAlchemyError:
        logging.error("Error adding book", exc_info=True)
        abort(500, description="Error adding book")

@app.route('/borrowers', methods=['GET'])
def list_borrowers():
    try:
        borrowers = Borrower.query.all()
        return jsonify([borrower.to_dict() for borrower in borrowers]), 200
    except SQLAlchemyError:
        logging.error("Error fetching borrowers", exc_info=True)
        abort(500, description="Error fetching borrowers")

@app.route('/borrowers', methods=['POST'])
@require_authentication
def add_borrower():
    try:
        data = request.json
        if not data or 'name' not in data:
            abort(400, description="Bad Request: 'name' is required")

        new_borrower = Borrower(name=data['name'])
        db.session.add(new_borrower)
        db.session.commit()
        return jsonify(new_borrower.to_dict()), 201
    except SQLAlchemyError:
        logging.error("Error adding borrower", exc_info=True)
        abort(500, description="Error adding borrower")

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    if not query:
        return jsonify([]), 200

    try:
        books = Book.query.filter((Book.title.ilike(f'%{query}%')) | 
                                  (Book.author.ilike(f'%{query}%'))).all()
        return jsonify([book.to_dict() for book in books]), 200
    except SQLAlchemyError:
        logging.error("Error searching books", exc_info=True)
        abort(500, description="Error searching books")

@app.route('/export', methods=['GET'])
@require_authentication
def export_database():
    try:
        books = Book.query.all()
        borrowers = Borrower.query.all()

        filename = os.path.join(EXPORT_DIR, f'database_export_{uuid.uuid4()}.csv')
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['type', 'id', 'title', 'author', 'name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for book in books:
                writer.writerow({'type': 'book', 'id': book.id, 'title': book.title, 'author': book.author})

            for borrower in borrowers:
                writer.writerow({'type': 'borrower', 'id': borrower.id, 'name': borrower.name})

        response = send_file(filename, as_attachment=True)

        # Clean up the file after sending
        os.remove(filename)

        return response
    except SQLAlchemyError:
        logging.error("Error exporting database", exc_info=True)
        abort(500, description="Error exporting database")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        abort(500, description="An unexpected error occurred")

# Database Initialization
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
    app.run()  # Do not specify debug=True here
