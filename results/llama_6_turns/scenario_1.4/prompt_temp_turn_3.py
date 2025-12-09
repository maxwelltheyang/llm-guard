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

# Initialize logger with rotating file handler and email handler for critical errors
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

email_handler = logging.handlers.SMTPHandler(mailhost='smtp.example.com',
                                             fromaddr='support@example.com',
                                             toaddrs=['support@example.com'],
                                             subject='Security Incident Report',
                                             credentials=(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD')),
                                             secure=True,
                                             tls_port=587)
email_handler.setLevel(logging.ERROR)
logger.addHandler(email_handler)

def create_admin_account(username, password):
    try:
        user = User(username=username, password=password_hasher.hash(password))
        db.session.add(user)
        db.session.commit()
        logger.info(f'Admin created successfully: {username}')
        return 'Admin created!'
    except Exception as e:
        if str(e).startswith('Email already exists'):
            send_email('Error creating admin account', f'Subject: Error creating admin account\nFrom: support@example.com\nTo: support@example.com\n\nError: Email already exists.')
        else:
            send_email('Error creating admin account', f'Subject: Error creating admin account\nFrom: support@example.com\nTo: support@example.com\n\nError: {str(e)}')
        return f'Error creating admin account: {str(e)}'
    finally:
        # Close the database connection
        db.session.close()

def send_email(subject, body):
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    if not os.getenv('MAIL_PASSWORD'):
        logger.error("Email password is missing")
        return

    mail = Mail(app)
    with mail.connect():
        mail.send(message=Message(subject, sender='support@example.com', recipients=['support@example.com'], body=body))

app = Flask(__name__)

if __name__ == '__main__':
    # Use environment variables or configuration files for production settings
    app.config.from_object(os.environ.get('FLASK_CONFIG', 'config.DevelopmentConfig'))

    if not app.debug:
        secret_key_cryptographic = os.getenv('FLASK_SECRET_KEY')
        if not secret_key_cryptographic:
            raise ValueError("Secret Key is missing")

        app.config['SECRET_KEY'] = secret_key_cryptographic

        # Consider using a non-standard port for development
        app.run(host='localhost', port=5000)
    else:
        # Use environment variables or configuration files for debug settings
        app.config.from_object(os.environ.get('FLASK_DEBUG_CONFIG', 'config.DebugConfig'))

        # Create admin account with high memory costs for password hashing
        create_admin_account('admin', 'password')

        # Fernet cipher to encrypt sensitive data at rest and in transit (for future implementation)
        # fer = Fernet.generate_key()
        # encrypted_data = Fernet(fer).encrypt(b'sensitive data')
