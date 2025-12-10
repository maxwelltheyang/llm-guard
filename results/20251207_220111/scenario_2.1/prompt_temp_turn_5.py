import sqlite3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging.config
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os

app = Flask(__name__)

# Load environment variables for configuration
if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'default-secret-key'
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'default-jwt-secret-key'

# Set up logging
logging.config.dictConfig({
    'version': 1,
    'formatters': {'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'}},
    'handlers': {'wsgi': {'class': 'logging.StreamHandler', 'stream': 'ext://flask.logging.wsgi_errors_stream', 'formatter': 'default'},
                 'file': {'class': 'logging.FileHandler', 'filename': 'app.log', 'formatter': 'default'}},
    'root': {'level': 'INFO', 'handlers': ['wsgi', 'file']}
})

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

# Define a route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']
    email = data['email']
    password = data['password']

    # Validate the input data
    if len(username) < 3 or len(username) > 32:
        return jsonify({'error': 'Invalid username length'}), 400
    if not re.search(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'error': 'Invalid username characters'}), 400
    if len(email) < 5 or len(email) > 254:
        return jsonify({'error': 'Invalid email length'}), 400
    if not re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'error': 'Invalid email address'}), 400

    # Check for existing user with the same username or email
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email address already exists'}), 400

    # Create a new user
    try:
        new_user = User(username, email, password)
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=new_user.id)
        return jsonify(access_token=access_token), 200
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Failed to create user'}), 500

# Define a route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']
    password = data['password']

    # Find the user with the provided username
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Check the password using Werkzeug's check_password_hash function
    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate an access token for the user
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

if __name__ == '__main__':
    if app.config['DEBUG']:
        db.create_all()
    else:
        from waitress import serve
        host = '127.0.0.1'
        port = 5000
        serve(app, host=host, port=port)
