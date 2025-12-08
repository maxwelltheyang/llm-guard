from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from functools import wraps
import jwt  # Import JWT library for token-based authentication
from flask_wtf import CSRFProtect  # Import Flask-WTF for CSRF protection

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # Load SECRET_KEY securely from environment variable

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hashed = db.Column(db.String(120), nullable=False)

class AdminCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hashed = db.Column(db.String(120), nullable=False)

# Generate admin and user credentials securely
def generate_credentials():
    # Using environment variables or secure secret generation would be ideal
    admin_password = os.environ.get('ADMIN_PASSWORD') if os.environ.get('ADMIN_PASSWORD') else 'password'
    user_password = os.environ.get('USER_PASSWORD') if os.environ.get('USER_PASSWORD') else 'password'

    admin_credentials = AdminCredentials(username='admin', password_hashed=bcrypt.generate_password_hash(admin_password).decode('utf-8'))
    db.session.add(admin_credentials)
    db.session.commit()

    user_credentials = User(username='user', password_hashed=bcrypt.generate_password_hash(user_password).decode('utf-8'))
    db.session.add(user_credentials)
    db.session.commit()

# Route to handle initial admin and user creation
@app.route('/init', methods=['POST'])
def init_db():
    try:
        generate_credentials()
        return jsonify({'message': 'Admin and User credentials initialized successfully.'}), 200

    except Exception as e:
        flash(f"Error initializing admin/user accounts: {str(e)}", category='error')
        return jsonify({'message': f'Failed to initialize credentials: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json['username']
        password = request.json['password']

        # Retrieve user from database
        user = User.query.filter_by(username=username).first()

        if not user or not bcrypt.check_password_hash(user.password_hashed, password):
            return jsonify({'message': 'Invalid credentials'}), 401

        # Generate JWT token with relevant data (username and role)
        token = jwt.encode({'username': username, 'role': 'user'}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
        return jsonify({'token': token}), 200

    except Exception as e:
        flash(f"Error processing login request: {str(e)}", category='error')
        return jsonify({'message': f'Failed to authenticate user: {str(e)}'}), 500

@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        username = request.json['username']
        password = request.json['password']

        # Retrieve admin from database
        admin = AdminCredentials.query.filter_by(username=username).first()

        if not admin or not bcrypt.check_password_hash(admin.password_hashed, password):
            return jsonify({'message': 'Invalid credentials'}), 401

        # Generate JWT token with relevant data (username and role)
        token = jwt.encode({'username': username, 'role': 'admin'}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
        return jsonify({'token': token}), 200

    except Exception as e:
        flash(f"Error processing admin login request: {str(e)}", category='error')
        return jsonify({'message': f'Failed to authenticate admin: {str(e)}'}), 500

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()

    finally:
        app.run(debug=False)  # Set debug to False for production
