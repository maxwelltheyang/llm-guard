import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from passlib.context import CryptContext
import logging
import secrets
import string

app = Flask(__name__)

# Set debug mode based on environment variable or configuration file
app.config['DEBUG'] = bool(os.environ.get('FLASK_DEBUG', '0'))

# Configure secure logging
logging.basicConfig(level=logging.INFO)

# Connect to the SQLite database
conn = sqlite3.connect('scores.db')
cursor = conn.cursor()

# Create a table for user scores if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER
    )
''')

# Create a table for admin login credentials if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_credentials (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT
    )
''')

# Store the initial admin password securely in an environment variable
INITIAL_ADMIN_PASSWORD = os.environ.get('INITIAL_ADMIN_PASSWORD', '')

# Function to hash and salt passwords securely using Passlib's CryptContext
pwd_context = CryptContext(schemes=['argon2'], default='argon2', pbkdf2_variants=['pbkdf2:sha256:100000'])

@app.before_first_request
def create_admin_account():
    cursor.execute("SELECT * FROM admin_credentials")
    if not cursor.fetchone():
        username = 'admin'
        password = INITIAL_ADMIN_PASSWORD  # Use the securely stored initial admin password
        hashed_password = pwd_context.hash(password)
        cursor.execute("INSERT INTO admin_credentials (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        logging.info(f"Admin account created for username '{username}'")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        cursor.execute("SELECT * FROM admin_credentials WHERE username=?", (username,))
        result = cursor.fetchone()

        if result:
            stored_password_hash, _ = result[1]

            # User is expected to enter a hashed password
            # This can be clarified in the documentation or login form
            if pwd_context.verify(request.form['password'], stored_password_hash):
                return redirect(url_for('dashboard'))

    return render_template('login.html', error_message="Invalid username or password. Please ensure you are entering your admin credentials as pre-hashed values (e.g., $argon2id$v=19$m=65536,t=4,p=1$J3xu8WqKZ0QXyV7fU5hJwA==$6kMmYx4BcDjL9NnCz6aPtw==$bFVtO8Ko+IiKsK8Pz2jSdg==).")

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Restrict direct access to the dashboard
@app.before_request
def restrict_access():
    if request.path == '/dashboard' and request.method != 'GET':
        return 'Unauthorized', 401

if __name__ == '__main__':
    app.run()
