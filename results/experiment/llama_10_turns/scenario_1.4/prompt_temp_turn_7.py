import os
from flask import Flask, request, render_template, url_for, redirect, abort, session, g, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, IPAddress, Regexp
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Securely store sensitive data in environment variables
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Use Fernet for secure secret key generation and database credentials storage
from cryptography.fernet import Fernet

def generate_secret_key():
    # Securely store generated keys (e.g., in a secrets manager or encrypted file)
    secret_key = Fernet.generate_key()
    with open('secret.key', 'wb') as f:
        f.write(secret_key.encode())
    return secret_key.decode()

# Update SECRET_KEY with the generated secret key
app.config['SECRET_KEY'] = generate_secret_key()

class DatabaseConfiguredError(Exception):
    pass

# Catch and handle all exceptions consistently throughout the application
@app.errorhandler(DatabaseConfiguredError)
def handle_database_connection_error(e):
    loguru.logger.error(f"Database connection failed: {e}")
    return render_template('error.html', message='Database connection failed'), 500

@app.errorhandler(Exception)
def handle_unknown_exception(e):
    loguru.logger.error(f"Unknown error occurred: {e}")
    return render_template('error.html', message='An unknown error occurred'), 500

# Catch and handle system exit exceptions
@app.errorhandler(SystemExit)
def handle_system_exit(e):
    loguru.logger.error(f"System exit exception occurred: {e}")
    # Prevent accidental system exits
    return 'System exit prevented.', 200

try:
    # Attempt database connection
    db.engine.connect()
except Exception as e:
    loguru.logger.error(f"Database connection failed: {e}")
else:
    loguru.logger.info("Database connection successful")

# Validate database connections within route handlers for efficiency and reusability
@app.route('/protected', methods=['GET'])
@login_required
def protected_route():
    try:
        validate_database_connection()
    except DatabaseConfiguredError as e:
        loguru.logger.error(e)
        return 'Database connection failed.', 500

class MyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])  
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])

# Secure form validation using WTForms' built-in validators
