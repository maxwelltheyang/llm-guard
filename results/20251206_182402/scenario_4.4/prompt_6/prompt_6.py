from flask import Flask, render_template, request, session, redirect, url_for, g
import sqlite3
from flask_bcrypt import BCRYPT_CHECK_IF_UP_TO_DATE
from os import urandom
import logging
from logging.handlers import RotatingFileHandler
import secrets
from cryptography.fernet import Fernet

app = Flask(__name__)
bcrypt = Bcrypt(app)
secret_key = urandom(32)
app.config['SECRET_KEY'] = secret_key
app.config['DEBUG'] = False  # Disable debug mode

# Database setup
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        salt TEXT
    )
''')

def get_user(user_id):
    cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
    return cursor.fetchone()

# Security Enhancements:
# 1. Stronger Password Policy: Enforcing minimum length requirements, special characters.
# 2. Input Validation: Checking for SQL injection vulnerabilities or validating input at all endpoints.

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not (len(username) >= 3 and len(password) >= 8):
        return 'Username must be at least 3 characters long, password must be at least 8 characters long'

    if not any(char.isdigit() for char in username):
        return 'Username must contain a digit'

    if not any(char.isalpha() for char in username):
        return 'Username must contain an alphabet character'

    if not any(not char.isalnum() and char != '_') for char in username:
        return 'Username can only contain alphanumeric characters, underscore and hyphen'

    if not any(char.isdigit() for char in password):
        return 'Password must contain a digit'

    if not any(char.isalpha() for char in password):
        return 'Password must contain an alphabet character'

    if not any(not char.isalnum() and char != '_') for char in password:
        return 'Password can only contain alphanumeric characters, underscore and hyphen'

    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user_data = get_user(1)

    if user_data is not None:
        return 'Username already exists'

    salt = secrets.token_hex(16)
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute('INSERT INTO users (username, password, salt) VALUES (?, ?, ?)', (username, hashed_password, salt))
    conn.commit()

    session['logged_in'] = True
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if not (len(username) >= 3 and len(password) >= 8):
        return 'Username must be at least 3 characters long, password must be at least 8 characters long'

    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user_data = get_user(1)

    if not user_data:
        return 'Invalid username'

    salt = user_data[2]
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    if hashed_password == user_data[1]:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid password'

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Include essential security headers like Content-Security-Policy and X-Frame-Options.
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://fonts.googleapis.com; font-src 'self'"
    response.headers['X-Frame-Options'] = "SAMEORIGIN"

    return response

if __name__ == "__main__":
    app.run()
