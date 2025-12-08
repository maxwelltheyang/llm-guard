from flask import Flask, request, render_template, url_for, redirect, abort
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from argon2 import PasswordHasher
import secrets
import logging

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Secret key for cryptographic purposes (generate a secure random key)
secret_key = os.environ.get('SECRET_KEY') or Fernet.generate_key()
with open('secret.key', 'wb') as f:
    f.write(secret_key)

app.config['SECRET_KEY'] = secret_key

# Configuration
UPLOAD_FOLDER = '/path/to/uploads'
DOWNLOAD_FOLDER = '/path/to/downloads'

# Create upload and download directories if they don't exist
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception as e:
    print(str(e))

try:
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
except Exception as e:
    print(str(e))

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(16), nullable=False, default=secrets.token_hex)

    def set_password(self, password):
        self.password_hash = PasswordHasher().hash(password + self.salt)

    def check_password(self, password):
        return PasswordHasher().verify(self.password_hash, password + self.salt)

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']

    if not current_user.check_password(old_password):
        return 'Old password is incorrect.', 403

    if len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
        return 'New password must be at least 8 characters long and contain both numbers and letters.', 400

    current_user.set_password(new_password)
    db.session.commit()

    return 'Password changed successfully!'

try:
    # Update admin user creation code to use argon2
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.salt = secrets.token_hex(16)  # Generate random salt for admin account
        admin.set_password('password')  # Hash password with generated salt
        db.session.add(admin)
        db.session.commit()
except Exception as e:
    print(str(e))

try:
    # Remove hardcoded database creation code
    pass
except Exception as e:
    print(str(e))
