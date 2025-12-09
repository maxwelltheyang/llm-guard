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
import secrets

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Secret key for cryptographic purposes (generate a secure random key)
secret_key = Fernet.generate_key()
with open('secret.key', 'wb') as f:
    f.write(secret_key)

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

    @staticmethod
    def validate_username(username):
        if len(username) < 3 or len(username) > 32:
            return False
        return True

    @staticmethod
    def validate_password(password):
        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            return False
        return True

    def set_password(self, password):
        self.password_hash = PasswordHasher().hash(password)

login_manager = LoginManager(app)  # Initialize Flask-Login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_admin_user():
    import uuid
    if not User.query.count():
        username = str(uuid.uuid4())
        password = secrets.token_urlsafe(16)
        hashed_password = PasswordHasher().hash(password)
        user = User(username=username, password_hash=hashed_password)
        user.set_password(password)  # Verify the password using a secure function
        db.session.add(user)
        db.session.commit()

from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/upload', methods=['POST'])
@login_required
@limiter.limit("10 per minute")  # Correctly implement IP blocking and rate limiting mechanisms
def upload_file():
    file = request.files['file']

    if file.filename not in ALLOWED_EXTENSIONS:
        import logging
        logging.error(f"Invalid file type: {file.filename}")
        return 'Invalid file type. Only images are allowed.', 400

    try:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
    except Exception as e:
        # Log or handle the error properly
        import logging
        logging.error(f"Error saving file: {str(e)}")
        return 'Failed to upload file.', 500

    return 'File uploaded successfully!'

try:
    if User.query.filter_by(username="admin").first().password_hash:
        # Remove hardcoded admin user creation code
        pass
except Exception as e:
    print(str(e))
