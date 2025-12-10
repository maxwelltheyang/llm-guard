import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlite3 import Error as SqliteError, connect
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, email_validator, EqualTo, ValidationError
from flask_wtf.csrf import CSRFProtect
from bleach import clean
import secrets
from logging.config import dictConfig
import logging

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },
                 'file': {
                     'class': 'logging.handlers.RotatingFileHandler',
                     'filename': 'app.log',
                     'maxBytes': 1024 * 1024 * 100,  # 100 MB
                     'backupCount': 10,
                     'formatter': 'default'
                 }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})

app = Flask(__name__)
csrf = CSRFProtect(app)

# Generate a secret key for secure session management
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

# Secure session management using Flask-Session
from flask_session import Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SSL/TLS for production environment
if os.environ.get('FLASK_ENV') == 'production':
    ssl_context = ('path/to/cert.pem', 'path/to/privkey.pem')
else:
    ssl_context = None

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = connect('database.db')
            c = conn.cursor()

            # Parameterized query to prevent SQL injection attacks
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()

            if user and check_password_hash(user[2], password):
                session['logged_in'] = True
                return redirect(url_for('index'))
        except SqliteError as e:
            logging.error(f"An error occurred: {e}")
            flash('Invalid input.', 'danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            conn = connect('database.db')
            c = conn.cursor()

            # Validate user input
            if len(username) < 3 or len(username) > 32:
                flash('Username must be between 3 and 32 characters.', 'danger')
            elif not username.replace('_', '-').replace('.', '').isalnum():
                flash('Username can only contain alphanumeric characters, underscores, and hyphens.', 'danger')

            # Parameterized query to prevent SQL injection attacks
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                      (username, email, generate_password_hash(password)))
            conn.commit()

            flash('Account created successfully!', 'success')
        except SqliteError as e:
            logging.error(f"An error occurred: {e}")
            flash('Invalid input.', 'danger')

    return render_template('register.html', form=form)

@app.route('/post', methods=['GET', 'POST'])
def post():
    form = PostForm()
    if request.method == 'POST':
        content = request.form['content']

        try:
            conn = connect('database.db')
            c = conn.cursor()

            # Validate user input
            if len(content) < 1 or len(content) > 4096:
                flash('Content must be between 1 and 4096 characters.', 'danger')

            # Parameterized query to prevent SQL injection attacks
            c.execute("INSERT INTO posts (content) VALUES (?)", 
                      (content,))
            conn.commit()

            flash('Post created successfully!', 'success')
        except SqliteError as e:
            logging.error(f"An error occurred: {e}")
            flash('Invalid input.', 'danger')

    return render_template('post.html', form=form)

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    app.run(host=host, port=port, ssl_context=ssl_context)
