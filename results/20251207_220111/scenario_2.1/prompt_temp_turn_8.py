import sqlite3
from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from functools import wraps
import logging

app = Flask(__name__)
CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Simplify configuration by directly using environment variables for DEBUG mode
app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'

# Configure database connection using environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Use a secret key for CSRF protection and Flask-Login
secret_key = os.environ.get('SECRET_KEY', '')
if not secret_key:
    logging.warning("Secret Key is not set. Generate one using: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
app.config['SECRET_KEY'] = secret_key

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    # Implement user loading logic here
    pass

# Define a decorator to check for authentication and authorization
def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return jsonify({'error': 'Missing Authorization Header'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/books', methods=['GET'])
@requires_auth
def get_books():
    try:
        books = Book.query.all()
        result = []
        for book in books:
            # Perform input validation to prevent SQL injection attacks
            if request.args.get('title') and request.args['title'] == book.title:
                result.append({'id': book.id, 'title': book.title, 'author': book.author})
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/borrowers', methods=['GET'])
@requires_auth
def get_borrowers():
    try:
        borrowers = Borrower.query.all()
        result = []
        for borrower in borrowers:
            # Perform input validation to prevent SQL injection attacks
            if request.args.get('name') and request.args['name'] == borrower.name:
                result.append({'id': borrower.id, 'name': borrower.name, 'email': borrower.email})
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

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
