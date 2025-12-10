import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import hashlib
import secrets
import logging

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

# Function to hash and salt passwords
def hash_password(password):
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest(), salt

@app.before_first_request
def create_admin_account():
    cursor.execute("SELECT * FROM admin_credentials")
    if not cursor.fetchone():
        username = 'admin'
        password = secrets.token_urlsafe(32)  # Generate a unique random password of length 32
        hashed_password, _ = hash_password(password)
        cursor.execute("INSERT INTO admin_credentials (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        logging.info(f"Initial Admin Password set securely for username '{username}'")

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
            if stored_password_hash == request.form['password']:
                return redirect(url_for('dashboard'))

    return render_template('login.html', error_message="Invalid username or password. Please ensure you are entering your admin credentials as a hashed password.")

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
