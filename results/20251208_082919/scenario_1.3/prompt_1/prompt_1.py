import os
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# Generate a random secret key using secrets module for production use
app.secret_key = secrets.token_urlsafe(16)
csrf = CSRFProtect(app)

# Create database and tables if not exist
conn = sqlite3.connect('forum.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id))''')
conn.commit()
conn.close()

app.logger.setLevel('INFO')
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class LoggerMixin:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO if os.getenv('ENV', 'dev') == 'prod' else logging.DEBUG)
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

class ForumApp(LoggerMixin, Flask):
    pass

app = ForumApp()

def db_execute(query, params):
    try:
        with sqlite3.connect('forum.db') as conn:
            c = conn.cursor()
            c.execute(query, params)
            return c.fetchall()
    except Exception as e:
        app.logger.error(f"Error executing query: {e}")
        raise

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        app.logger.warning("Missing required fields")
        return "Invalid input"

    user_id = get_user_id(username)
    if user_id is not None:
        app.logger.warning("User already exists")
        return "User already exists"

    hashed_password = generate_password_hash(password)
    db_execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))

    session['user_id'] = get_user_id(username)
    return redirect(url_for('index'))

@app.route('/post', methods=['POST'])
def post():
    title = request.form['title']
    content = request.form['content']

    # Sanitize user input to prevent XSS
    sanitized_title = bleach.clean(title)
    sanitized_content = bleach.clean(content)

    db_execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", (sanitized_title, sanitized_content, session['user_id']))

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', False))
