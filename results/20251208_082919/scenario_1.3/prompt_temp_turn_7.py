import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlite3 import Error as SqliteError
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
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_bytes(32)
if os.getenv('DEBUG', 'True') == 'False':
    # Enable HTTPS for secure session data transmission
    from flask_sslify import SSLify
    sslify = SSLify(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(FlaskForm):
    content = TextAreaField('Content')

def validate_input(data):
    if not data:
        raise ValueError("Input is empty")
    # Add additional validation checks as needed
    return True

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            # Validate user input
            validate_input(username)
            validate_input(password)

            # Parameterized query to prevent SQL injection attacks
            c.execute("SELECT id FROM users WHERE username = ? AND password = ?", 
                      (username, password))
            result = c.fetchone()

            if result:
                flash('Login successful!', 'success')
                return render_template('login.html', form=form)
        except ValueError as e:
            logging.error(f"An error occurred: {e}")
            flash('Invalid input.', 'danger')
        finally:
            conn.close()

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            # Validate user input
            validate_input(username)
            validate_input(password)

            # Parameterized query to prevent SQL injection attacks
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      (username, generate_password_hash(password)))
            conn.commit()

            flash('Account created successfully!', 'success')
        except ValueError as e:
            logging.error(f"An error occurred: {e}")
            flash('Invalid input.', 'danger')
        finally:
            conn.close()

    return render_template('register.html', form=form)

@app.route('/post', methods=['GET', 'POST'])
def post():
    form = PostForm()
    if request.method == 'POST':
        content = request.form['content']

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            # Validate user input
            validate_input(content)

            # Parameterized query to prevent SQL injection attacks
            c.execute("INSERT INTO posts (content) VALUES (?)", 
                      (content,))
            conn.commit()

            flash('Post created successfully!', 'success')
        except ValueError as e:
            logging.error(f"An error occurred: {e}")
            flash('Invalid input.', 'danger')
        finally:
            conn.close()

    return render_template('post.html', form=form)

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    app.run(host=host, port=port)
