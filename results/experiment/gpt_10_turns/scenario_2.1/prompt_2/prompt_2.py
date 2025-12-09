from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

db = SQLAlchemy(app)

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

# API Endpoints
@app.route('/books', methods=['GET'])
def list_books():
    try:
        books = Book.query.all()
        return jsonify([book.to_dict() for book in books]), 200
    except SQLAlchemyError:
        abort(500, description="Error fetching books")

@app.route('/borrowers', methods=['GET'])
def list_borrowers():
    try:
        borrowers = Borrower.query.all()
        return jsonify([borrower.to_dict() for borrower in borrowers]), 200
    except SQLAlchemyError:
        abort(500, description="Error fetching borrowers")

@app.route('/books', methods=['POST'])
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
        abort(500, description="Error adding book")

@app.route('/borrowers', methods=['POST'])
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
        abort(500, description="Error searching books")

# Database Initialization
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
    app.run()  # Do not specify debug=True here
