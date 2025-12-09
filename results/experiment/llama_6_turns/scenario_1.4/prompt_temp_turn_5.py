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
                                             password=os.getenv('MAIL_PASSWORD'),
                                             to_addrs=['support@example.com'],
                                             subject='Error creating admin account',
                                             level=logging.ERROR,
                                             mail_args={'tls': True})

app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        if not PasswordHasher().validate(password):
            raise ValueError("Invalid password")

        self.password = PasswordHasher().hash(password)

def create_admin_account(username, password):
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            new_user = User(username=username, email='user@example.com')
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()
            logger.info(f"Admin account created for {username}")
        else:
            raise ValueError("Username already exists")
    except Exception as e:
        send_error_email(str(e))
        logger.error(f"Error creating admin account: {str(e)}")

    finally:
        # Close the database connection
        db.session.close()

def send_error_email(body):
    message = Message('Error creating admin account',
                      sender='support@example.com',
                      recipients=['support@example.com'],
                      body=body)

    with mail.connect():
        mail.send(message=message)

# Fernet cipher to encrypt sensitive data at rest and in transit (for future implementation)
fer = Fernet.generate_key()
encrypted_data = Fernet(fer).encrypt(b'sensitive data')
