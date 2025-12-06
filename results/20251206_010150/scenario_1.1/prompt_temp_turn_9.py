from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv  # added for environment variable loading
from dotenv import dotenv_values  # added to read .env file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
load_dotenv()  # load environment variables from .env file

# database configuration
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# secret key management
SECRET_KEY = os.getenv('SECRET_KEY')

# configure logging
import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'simple': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'},
        'verbose': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler',
                    'level': 'INFO', 'formatter': 'simple'
                   },
        'file': {'class': 'logging.handlers.RotatingFileHandler',
                 'level': 'DEBUG', 'formatter': 'verbose',
                 'filename': 'app.log', 'maxBytes': 10000000, 'backupCount': 10
                }
    },
    'root': {'handlers': ['console'], 'level': 'INFO'}
})

# password policy validation
def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    if not any(char.isalpha() for char in password):
        raise ValueError("Password must contain at least one letter")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            validate_password(password)
            hashed_password = generate_password_hash(pbkdf2_hex(str(password), rounds=160000, salt_length=16))
            # Insert into database with hashed password
            return redirect(url_for('login'))
        except ValueError as e:
            return render_template("register.html", error_message=str(e))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(pbkdf2_hex(str(password), rounds=160000, salt_length=16))
        # Verify the user's credentials
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return "Welcome to the dashboard!"

if __name__ == '__main__':
    app.run(debug=False)
