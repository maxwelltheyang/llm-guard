import sqlite3
from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from functools import wraps
import logging
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app = Flask(__name__)
CSRFProtect(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Simplify configuration by directly using environment variables for DEBUG mode and secret key
app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Configure database connection using environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define a decorator to check for authentication and authorization
def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if not access_token:
            return jsonify({'error': 'Missing Authorization Header'}), 401
        try:
            jwt.decode(access_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return jsonify({'error': 'Invalid Token'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.password == password:
        return jsonify({'error': 'Invalid Credentials'}), 401
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

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
