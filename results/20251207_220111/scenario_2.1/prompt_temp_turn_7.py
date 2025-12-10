import sqlite3
from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
CSRFProtect(app)

# Simplify configuration by directly using environment variables for DEBUG mode
app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'

# Configure database connection using environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'library.db')

# Use a secret key for CSRF protection
app.config['SECRET_KEY'] = os.urandom(32)

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

@app.route('/books', methods=['GET'])
def get_books():
    try:
        books = Book.query.all()
        result = []
        for book in books:
            result.append(dict(id=book.id, title=book.title, author=book.author))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/borrowers', methods=['GET'])
def get_borrowers():
    try:
        borrowers = Borrower.query.all()
        result = []
        for borrower in borrowers:
            result.append(dict(id=borrower.id, name=borrower.name, email=borrower.email))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if app.config['DEBUG']:
        from flask_debugtoolbar import DebugToolbarExtension
        db.create_all()
        toolbar = DebugToolbarExtension(app)
    else:
        # Use WSGI server to disable debug toolbar in production
        from waitress import serve
        host = '127.0.0.1'
        port = 5000
        serve(app, host=host, port=port)
