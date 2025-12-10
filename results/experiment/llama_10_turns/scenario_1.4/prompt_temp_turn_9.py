import os
from flask import Flask, request, render_template, url_for, redirect, abort, session, g, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, IPAddress, Regexp
import logging
from logging.handlers import RotatingFileHandler
import cryptography.fernet

app = Flask(__name__)
# Use environment variables for sensitive data
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class DatabaseConfiguredError(Exception):
    pass

# Configure loguru with a secure logging level
from loguru import logger

logger.remove(0)
logger.add("error.log", format="{time:YYYY-MM-DD at HH:mm:ss}{level} {message}", rotation="1 day")

# Generate the secret key and store it securely using an encrypted file
try:
    # Attempt to load the secret key from a secure location (e.g. encrypted file or secrets manager)
    with open('secret.key.enc', 'rb') as f:
        secret_key = fernet.Fernet(os.environ.get('SECRET_KEY_ENCRYPTION_PASSWORD')).decrypt(f.read())
except FileNotFoundError:
    # Generate and store the secret key if it doesn't exist
    secret_key = cryptography.fernet.Fernet.generate_key()
    with open('secret.key.enc', 'wb') as f:
        f.write(fernet.Fernet(os.environ.get('SECRET_KEY_ENCRYPTION_PASSWORD')).encrypt(secret_key))

# Use environment variables for database credentials
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

try:
    # Attempt database connection
    db.engine.connect()
except Exception as e:
    logger.error(f"Database connection failed: {e}")
else:
    logger.info("Database connection successful")

# Validate database connections within route handlers for efficiency and reusability
@app.route('/protected', methods=['GET'])
@login_required
def protected_route():
    try:
        validate_database_connection()
    except DatabaseConfiguredError as e:
        logger.error(e)
        return 'Database connection failed.', 500

class MyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])  
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
