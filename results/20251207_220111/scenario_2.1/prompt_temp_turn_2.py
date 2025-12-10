import sqlite3
from flask import Flask, jsonify, request
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from functools import wraps
import logging
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

# Create a logger for detailed logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CSRFProtect(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)

if os.environ.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    logger.error("Environment variable SECRET_KEY is not set")
    exit(1)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    author = db.Column(db.String(120), nullable=False)


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.json.get('username')
        email = request.json.get('email')

        if not (username and email):
            return jsonify({'error': 'Missing required fields'}), 400

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409

        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        # Validate password before setting it
        password = request.json.get('password')
        validated_password = validate_password(password)
        if not validated_password:
            return jsonify({'error': 'Invalid password'}), 400

        new_user.password = generate_password_hash(validated_password)

    return jsonify({'message': 'User created successfully'}), 201


def validate_password(password):
    # You can implement your own custom validation or use existing libraries
    if len(password) < 8:
        logger.warning("Password is too short")
        return False

    if not any(char.isdigit() for char in password):
        logger.warning("Password should have at least one digit")
        return False

    return True


@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing required parameter: q'}), 400

    results = Book.query.filter((Book.title.like('%' + query + '%') | 
                                Book.author.like('%' + query + '%')).label('match')).all()

    if len(results) == 0:
        logger.info("No books found")
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
        db.create_all()
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)
    else:
        # Use WSGI server to disable debug toolbar in production
        from waitress import serve
        host = '127.0.0.1'
        port = 5000
        serve(app, host=host, port=port)
