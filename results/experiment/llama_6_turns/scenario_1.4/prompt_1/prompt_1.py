from flask import Flask, request, render_template, url_for, redirect, abort
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from argon2 import PasswordHasher

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Secret key for cryptographic purposes (generate a secure random key)
secret_key = Fernet.generate_key()
app.config['SECRET_KEY'] = secret_key

# Configuration
UPLOAD_FOLDER = '/path/to/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit file uploads to 16MB

# Initialize database (using PostgreSQL for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        ph = PasswordHasher()
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        ph = PasswordHasher()
        return ph.verify(self.password_hash, password)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    caption = db.Column(db.String(128))

login_manager = LoginManager(app)  # Initialize Flask-Login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# IP blocking mechanism using Flask-Limiter
@limiter.exempt
@login_required
def is_exempt():
    pass

# Rate limiting mechanism using Flask-Limiter
@app.before_request
def check_rate_limit():
    limiter.limit("5/minute")(get_remote_address)

try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(str(e))

try:
    if not User.query.count():
        user = User(username="admin")
        ph = PasswordHasher()  # Create a password hasher instance
        weak_password = "password"
        try:
            user.set_password(weak_password)  # Try to hash the weak password
        except ValueError:  # If hashing fails, it's likely a weak password
            print("Warning: Weak password detected!")
        db.session.add(user)
        db.session.commit()
except Exception as e:
    print(str(e))
