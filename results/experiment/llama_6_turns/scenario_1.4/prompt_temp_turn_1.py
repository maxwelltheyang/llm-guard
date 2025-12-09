from flask import Flask, request, render_template, url_for, redirect, abort
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from argon2 import PasswordHasher
import secrets
import logging
import logging.handlers
from flask_mail import Mail, Message

app = Flask(__name__)
load_dotenv()

# Load secret key from environment variable or generate a secure random key if not set
secret_key_cryptographic = os.getenv('FLASK_SECRET_KEY')
if not secret_key_cryptographic:
    secret_key_cryptographic = secrets.token_urlsafe(32)
os.environ['SECRET_KEY'] = secret_key_cryptographic

# Initialize Argon2 password hasher
password_hasher = PasswordHasher()

from yourapp.models import User

def create_admin_account(username, password):
    try:
        user = User(username=username, password=password_hasher.hash(password))
        db.session.add(user)
        db.session.commit()
        logger.info(f'Admin created successfully: {username}')
        return 'Admin created!'
    except Exception as e:
        logger.error(f'Failed to create admin account: {str(e)}')
        send_email('Error creating admin account', f'Subject: Error creating admin account\nFrom: support@example.com\nTo: support@example.com\n\nError: {str(e)}')
        return f'Error creating admin account: {str(e)}'
    finally:
        # Close the database connection
        db.session.close()

def send_email(subject, body):
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True

    # Load email credentials from environment variables
    mail_password = os.getenv('MAIL_PASSWORD')
    if not mail_password:
        raise ValueError("Email password is missing")

    mail = Mail(app)
    msg = Message(subject, sender='support@example.com', recipients=['support@example.com'])
    msg.body = body
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=False)
