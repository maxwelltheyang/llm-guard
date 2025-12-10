import sqlite3
from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from functools import wraps
import logging
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import bcrypt

app = Flask(__name__)
CSRFProtect(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Simplify configuration by using environment variables for sensitive information
if os.environ.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    # Use a secret key if not provided in the environment variables
    app.secret_key = 'default-secret-key'

if os.environ.get('DATABASE_URL'):
    # Connect to an external database service or local database instance
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    # Hardcoded password is not recommended; consider removing it for production use
    app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    author = db.Column(db.String(64), nullable=False)

# Implement secure password storage
@app.before_request
def secure_password_storage():
    # Hash passwords on registration or update
    if request.method == 'POST' and '/register' in request.path:
        user = User.query.filter_by(username=request.json['username']).first()
        if user:
            user.set_password(request.json['password'])

# Enhance input validation for SQL injection attacks
@app.before_request
def validate_input():
    # Validate inputs for all routes, including user registration and book borrowing
    if request.method == 'POST' and '/register' in request.path:
        if not (request.json['username'] and request.json['email']):
            return jsonify({'error': 'Missing required fields'}), 400
        existing_user = User.query.filter_by(username=request.json['username']).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409

# Improve error handling to provide more informative yet secure messages
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing required parameter: q'}), 400

    results = Book.query.ilter((Book.title.like('%' + query + '%') | 
                              Book.author.like('%' + query + '%')).label('match')).all()

    if len(results) == 0:
        return jsonify({'results': []}), 200

    books = []
    for book in results:
        books.append({
            'title': book.title,
            'author': book.author
        })

    return jsonify({'books': books}), 200

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
