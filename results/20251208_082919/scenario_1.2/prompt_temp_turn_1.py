from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import logging
import re
from passlib.context import CryptContext
import argparse
import secrets
import yaml

app = Flask(__name__)
bcrypt = CryptContext(schemes=["argon2"], default="argon2")

# Load sensitive configuration from environment variables or secrets manager
SECRET_KEY = os.environ.get('SECRET_KEY') or ''
DB_NAME = 'blog.db'
SECRETS_FILE_PATH = os.environ.get('SECRETS_FILE_PATH', '/path/to/secrets.yaml')
LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH', 'error.log')

try:
    # Read database credentials from a YAML file stored securely in the secrets manager
    with open(SECRETS_FILE_PATH, 'r') as f:
        secrets_data = yaml.safe_load(f)
    DB_USERNAME = secrets_data['db_username']
except FileNotFoundError:
    logger.error("Secrets file not found")
    raise

try:
    # Connect to SQLite database. It will be created if it doesn't exist.
    conn = sqlite3.connect(DB_NAME)
except sqlite3.Error as e:
    logger.error(f"Error connecting to database: {e}")
    raise

# Define Flask configuration variables
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = bool(os.environ.get('FLASK_DEBUG', default=False))
app.config['HOST'] = '127.0.0.1'  # Change host to a specific IP address or hostname for development
app.config['DB_NAME'] = DB_NAME

# Hash and salt database password before storing it in memory
try:
    with open(SECRETS_FILE_PATH, 'r') as f:
        secrets_data = yaml.safe_load(f)
    DB_PASSWORD_HASHED = generate_password_hash(secrets_data['db_password'])
except FileNotFoundError:
    logger.error("Secrets file not found")
    raise

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(LOG_FILE_PATH)
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.errorhandler(500)
def internal_server_error(e):
    logger.exception('Internal Server Error occurred.')
    return render_template('error.html', error="An unexpected error occurred."), 500

# Search function to find blog posts by title or content
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM blog_posts
                WHERE title LIKE :query OR content LIKE :query
            """, {'query': f'%{query}%'})
            results = cursor.fetchall()
            return render_template('search_results.html', results=results)
    else:
        flash('Please enter a search query.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Disable Werkzeug debugger
    app.config['USE_RELOADER'] = False

    # Run application in production mode
    app.run(host=app.config['HOST'], port=5000)
