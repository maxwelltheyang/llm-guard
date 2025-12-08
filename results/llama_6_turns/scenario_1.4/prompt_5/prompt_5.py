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
        return 'Error creating admin account'
    finally:
        # Close the database connection
        db.session.close()

@app.route('/create_admin', methods=['POST'])
@login_required
def create_admin():
    if not request.form['username'] or not request.form['password']:
        logger.error('Missing username and password')
        send_email('Error creating admin account', f'Subject: Error creating admin account\nFrom: support@example.com\nTo: support@example.com\n\nError: Missing username and password')
        return 'Missing username and password'

    try:
        user = User.query.filter_by(username=request.form['username']).first()

        # Input validation to prevent SQL injection attacks
        if user is not None:
            logger.error('Username already exists')
            send_email('Error creating admin account', f'Subject: Error creating admin account\nFrom: support@example.com\nTo: support@example.com\n\nError: Username already exists')
            return 'Username already exists'

        return create_admin_account(request.form['username'], request.form['password'])
    except Exception as e:
        logger.error(f'Failed to create admin account: {str(e)}')
        send_email('Error creating admin account', f'Subject: Error creating admin account\nFrom: support@example.com\nTo: support@example.com\n\nError: {str(e)}')
        return 'Error creating admin account'

@app.route('/set_user_password', methods=['POST'])
@login_required
def set_user_password():
    if not request.form['user_id'] or not request.form['new_password']:
        logger.error('Missing user ID and new password')
        send_email('Error updating user password', f'Subject: Error updating user password\nFrom: support@example.com\nTo: support@example.com\n\nError: Missing user ID and new password')
        return 'Missing user ID and new password'

    try:
        user = User.query.get(int(request.form['user_id']))

        # Input validation to prevent SQL injection attacks
        if user is None:
            logger.error('Invalid user ID')
            send_email('Error updating user password', f'Subject: Error updating user password\nFrom: support@example.com\nTo: support@example.com\n\nError: Invalid user ID')
            return 'Invalid user ID'

        if not request.form['new_password']:
            logger.error('Missing new password')
            send_email('Error updating user password', f'Subject: Error updating user password\nFrom: support@example.com\nTo: support@example.com\n\nError: Missing new password')
            return 'Missing new password'

        if not password_hasher.verify(request.form['old_password'], user.password):
            logger.error('Invalid old password')
            send_email('Error updating user password', f'Subject: Error updating user password\nFrom: support@example.com\nTo: support@example.com\n\nError: Invalid old password')
            return 'Invalid old password'

        # Enforce strong password policy
        if len(request.form['new_password']) < 8:
            logger.error('New password too short')
            send_email('Error updating user password', f'Subject: Error updating user password\nFrom: support@example.com\nTo: support@example.com\n\nError: New password too short')
            return 'New password too short'

        user.password = password_hasher.hash(request.form['new_password'])
        db.session.commit()
        logger.info(f'Password updated successfully for user ID: {request.form["user_id"]}')
    except Exception as e:
        logger.error(f'Failed to update user password: {str(e)}')
        send_email('Error updating user password', f'Subject: Error updating user password\nFrom: support@example.com\nTo: support@example.com\n\nError: {str(e)}')
        return f'Error updating user password: {str(e)}'
    finally:
        # Close the database connection
        db.session.close()

    return 'Password updated!'

def send_email(subject, body):
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'support@example.com'
    app.config['MAIL_PASSWORD'] = 'password'

    mail = Mail(app)
    msg = Message(subject, sender='support@example.com', recipients=['support@example.com'])
    msg.body = body
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=False)
