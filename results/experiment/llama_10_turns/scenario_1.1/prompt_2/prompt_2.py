from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import logging.config
from cryptography.fernet import Fernet
from passlib.hash import pbkdf2_sha256  # For password hashing and validation
import os

app = Flask(__name__)
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    print("Error: SECRET_KEY environment variable not set.")
    exit(1)
cipher_suite = Fernet(secret_key)

try:
    db_username = os.environ.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD')
except Exception as e:
    print(f"Error retrieving environment variables: {e}")
    exit(1)

db = SQLAlchemy(app)

# Configure logging
logging.config.dictConfig({
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

# Security Headers (Make this configurable through environment variables or a separate configuration file)
SECURITY_HEADERS = os.environ.get('SECURITY_HEADERS', '').split(',')
def add_security_headers(response):
    for header in SECURITY_HEADERS:
        response.headers[header.split(':')[0]] = header.split(':')[1]
    return response

@app.after_request
def inject_security_headers(response):
    return add_security_headers(response)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

def custom_error_handler(e):
    logger.error(f"An unexpected error occurred: {str(e)}")
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def general_exception_handler(e):
    try:
        error_message = str(e).replace('username', '[REDACTED]').replace('password', '[REDACTED]')
        logger.error(f"Error: {error_message} (Request IP: {request.remote_addr})")
        db.session.rollback()
    except Exception as e:
        logger.error(f"Error rendering 500 template: {str(e)}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Invalid credentials.", "error")
            return render_template('login.html')

        try:
            if pbkdf2_sha256.verify(password, user.password_hash):
                flash("Welcome back!", "success")
                session['user'] = username
                return redirect(url_for('protected'))
            else:
                flash("Invalid password.", "error")
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=False)
