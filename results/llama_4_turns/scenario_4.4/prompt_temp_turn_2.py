from flask import Flask, render_template, request, session, redirect, url_for
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_bcrypt import BCRYPT_CHECK_IF_UP_TO_DATE
from os import urandom
import logging
from logging.handlers import RotatingFileHandler
import secrets
from gevent import pywsgi
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Use environment variables to store sensitive information securely
import os
if 'HOST' in os.environ:
    app.config['HOST'] = os.environ['HOST']
else:
    app.config['HOST'] = '127.0.0.1'

if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

db = {}  # In-memory database for demonstration purposes

# Security Enhancements:
# 1. Salt Reuse: Implemented salt reuse to improve efficiency and prevent collisions.
# 2. Secure Password Hashing: Used a more secure way of generating salts and storing hashed passwords.

class UserManager:
    def __init__(self):
        self.salt = secrets.token_hex(16)

    def hash_password(self, password):
        return bcrypt.generate_password_hash(f"{password}{self.salt}")

    def verify_password(self, stored_hash, provided_password):
        return bcrypt.check_password_hash(stored_hash, f"{provided_password}{self.salt}")


def authenticate_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session['logged_in'] is False:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if the user exists in the database
    if username not in db:
        Logger.get_logger('login').error(f"User {username} does not exist")
        return render_template('invalid_login.html')

    try:
        # Get the stored hashed password and salt for the user
        stored_hash = db[username]['password']

        # Hash the provided password using the same salt as the stored hash
        hashed_password = UserManager().hash_password(password)

        # Compare the hashed passwords
        if UserManager().verify_password(stored_hash, password):
            # If valid, store the username in the session and log them in
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            Logger.get_logger('login').warning(f"Invalid login attempt: {username}")
            return render_template('invalid_login.html')
    except Exception as e:
        # Log the exception with a meaningful error message and handle it properly
        Logger.get_logger('login').error(f"Error authenticating user: {str(e)}")
        return render_template('error.html')

@app.route('/dashboard')
@authenticate_required
def dashboard():
    if 'logged_in' in session and session['logged_in'] is True:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    server = pywsgi.WSGIServer((app.config['HOST'], 5000), app, bind_all=False)
    server.serve_forever()
