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
# 1. Database Storage: Using SQLite as the database for secure storage of user credentials.
# 2. Authentication Flow: Generating a new random salt each time and storing both the hashed password and salt together in the database.

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return 'Username and password required'

    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    if get_user(1):
        return 'Username taken'

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

    if not username or not password:
        return 'Username and password required'

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

if __name__ == "__main__":
    app.run(debug=True)
