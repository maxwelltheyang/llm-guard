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

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Secret key for cryptographic purposes (generate a secure random key)
secret_key_cryptographic = Fernet.generate_key()
with open('cryptographic.key', 'wb') as f:
    f.write(secret_key_cryptographic)

# Secret key for Flask (store in environment variable)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

try:
    from yourapp import create_tables

except Exception as e:
    print(str(e))

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = PasswordHasher().hash(password)

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f'An error occurred: {e}')
    return 'An unexpected error occurred.', 500

ph = PasswordHasher()

@app.route('/set_user_password', methods=['POST'])
@login_required
def set_user_password():
    if not request.form['user_id'] or not request.form['new_password']:
        return 'Missing user credentials.', 400

    try:
        # Validate the new password using a secure library (argon2)
        if not ph.verify(request.form['new_password'], None):
            raise Exception('Invalid password')

        # Update the user's password
        user = User.query.get(int(request.form['user_id']))
        user.set_password(request.form['new_password'])

    except Exception as e:
        logging.error(f'Failed to update user password: {e}')
        return f'Failed to update user password: {str(e)}', 400

    finally:
        logging.info(f'User password updated: {request.form["user_id"]}')

    return 'Password updated!'

@app.route('/create_admin_account', methods=['POST'])
def create_admin_account():
    if not request.form['username'] or not request.form['password']:
        return 'Missing admin credentials.', 400

    try:
        # Validate the new password using a secure library (argon2)
        if not ph.verify(request.form['password'], None):
            raise Exception('Invalid password')

        # Create an admin account programmatically
        user = User(username=request.form['username'])
        user.set_password(request.form['password'])

    except Exception as e:
        logging.error(f'Failed to create admin account: {e}')
        return f'Failed to create admin account: {str(e)}', 400

    finally:
        logging.info(f'Admin created successfully: {request.form["username"]}')

    return 'Admin created!'

if __name__ == '__main__':
    app.run(debug=False)
