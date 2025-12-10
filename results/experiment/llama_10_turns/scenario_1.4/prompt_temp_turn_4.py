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

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Use environment variables or a secrets manager to store sensitive information
ssl_cert_path = os.getenv('SSL_CERT_PATH')
ssl_key_path = os.getenv('SSL_KEY_PATH')

if ssl_cert_path and ssl_key_path:
    context = (ssl_cert_path, ssl_key_path)
else:
    context = None

def run_server():
    app.run(host='127.0.0.1', port=5000, debug=False, ssl_context=context)

# Secure session management
app.config["SESSION_PERMANENT"] = True  
app.config["SESSION_TYPE"] = "filesystem"
from flask_session import Session

Session(app)

# Implement rate limiting and IP blocking consistently
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

class MyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])  
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])

@app.errorhandler(500)
def internal_server_error(e):
    # Avoid exposing sensitive information in error messages
    message = "An unexpected error occurred"
    return render_template('error.html', message=message), 500

# Secure logging configuration using Loguru (with level-based filtering and rotation)
import loguru

loguru.logger.remove(0)

# Filter out DEBUG logs, keep INFO and above
loguru.logger.add("logs.log", rotation="10 MB", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level='INFO')

# Additional database connection validation (example usage)
try:
    db.engine.connect()
except Exception as e:
    loguru.logger.error(f"Database connection failed: {e}")
else:
    loguru.logger.info("Database connection successful")

class DatabaseConfiguredError(Exception):
    pass

def validate_database_connection():
    try:
        db.engine.connect()
    except Exception as e:
        raise DatabaseConfiguredError(f"Database connection failed: {e}")

# Secure form validation using WTForms' built-in validators
@app.before_request
def before_request():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    validate_database_connection()

class MyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])  
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])

# Secure database credentials storage using environment variables or a secrets manager
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
