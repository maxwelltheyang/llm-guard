from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import logging
import re

# Configure logging for database errors
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load sensitive configuration from environment variables or secrets manager
SECRET_KEY = os.environ.get('SECRET_KEY') or ''
DEBUG_MODE = bool(os.environ.get('FLASK_DEBUG', default=False))
DB_NAME = 'blog.db'
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

try:
    # Connect to SQLite database. It will be created if it doesn't exist.
    conn = sqlite3.connect(DB_NAME)
except sqlite3.Error as e:
    logger.error(f'Database error: {e}')
    flash(f'Database error: {e}', category='error')
    return render_template('error.html'), 500

c = conn.cursor()

# Create table for users
try:
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username text NOT NULL, password_hash text NOT NULL)''')
except sqlite3.Error as e:
    logger.error(f'Database error: {e}')
    flash(f'Database error: {e}', category='error')
    return render_template('error.html'), 500

# Create table for posts
try:
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title text NOT NULL, content text NOT NULL)''')
except sqlite3.Error as e:
    logger.error(f'Database error: {e}')
    flash(f'Database error: {e}', category='error')
    return render_template('error.html'), 500

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("\d", password):
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate and sanitize user input
        if not validate_password(password):
            flash('Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one digit.', category='error')
            return render_template('register.html')

        username = re.sub(r'\s+', '', username)  # Remove whitespace from username
        try:
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = c.fetchone()
            if existing_user:
                flash('Username already exists. Please choose a different username.', category='error')
                return render_template('register.html')
        except sqlite3.Error as e:
            logger.error(f'Database error: {e}')

        try:
            hashed_password = generate_password_hash(password)
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f'Database error: {e}')
            flash(f'Database error: {e}', category='error')
            return render_template('error.html'), 500

        flash('User created successfully!', category='success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # Validate and sanitize user input
        if not title or not content:
            flash('Title and content are required.', category='error')
            return redirect(url_for('create_post'))

        try:
            c.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f'Database error: {e}')
            flash(f'Database error: {e}', category='error')
            return render_template('error.html'), 500

        flash('Post created successfully!', category='success')
        return redirect(url_for('view_posts'))
    return render_template('create_post.html')

@app.route('/view_posts')
def view_posts():
    try:
        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        return render_template('view_posts.html', posts=posts)
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
        flash(f'Database error: {e}', category='error')
        return render_template('error.html'), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
