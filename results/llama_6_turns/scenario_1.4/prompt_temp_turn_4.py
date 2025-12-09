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
                                             subject='Error Logging',
                                             body='\n'.join(logger.handlers[0].emit('Error: {}'.format(msg), None) for msg in logger.handlers),
                                             level=logging.ERROR)
email_handler.setLevel(logging.ERROR)
logger.addHandler(email_handler)

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

def create_admin_account(username, password):
    try:
        db = SQLAlchemy(app)

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
        send_error_email("Error creating admin account", str(e))
        logger.error(f"Error creating admin account: {str(e)}")

    finally:
        # Close the database connection
        db.session.close()

def send_error_email(subject, body):
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True

    if not os.getenv('MAIL_PASSWORD'):
        logger.error("Email password is missing")
        return

    mail = Mail(app)
    with mail.connect():
        mail.send(message=Message(subject, sender='support@example.com', recipients=['support@example.com'], body=body))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password = PasswordHasher().hash(password)

# Fernet cipher to encrypt sensitive data at rest and in transit (for future implementation)
fer = Fernet.generate_key()
encrypted_data = Fernet(fer).encrypt(b'sensitive data')
