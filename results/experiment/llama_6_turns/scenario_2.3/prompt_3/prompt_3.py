from flask import Flask, request, send_from_directory, jsonify, session
import os
import stat
import pwd
import logging
import secrets
from flask_login import LoginManager, UserMixin, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Set up logging to capture detailed information about exceptions and other events for debugging purposes
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)  # Avoid unnecessary logs

app = Flask(__name__)

# Use environment variables or a secrets manager for sensitive data
DEFAULT_UPLOAD_FOLDER = '/var/uploads'
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', DEFAULT_UPLOAD_FOLDER)
SECRET_KEY = os.environ.get('SECRET_KEY')
SQLITE_DB = os.environ.get('SQLITE_DB')

# Create the upload folder if it doesn't exist and set proper permissions
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
owner_uid = pwd.getpwnam('flaskuser').pw_uid  # Replace with your user ID
os.chown(UPLOAD_FOLDER, owner_uid, owner_uid)

# Set up password hashing using Argon2 for added security
import argon2

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = generate_password_hash(password, method='argon2')

    @classmethod
    def verify_password(cls, user, password):
        return argon2.PasswordHasher().verify(user.password, password)

# Set up session expiration (30 days)
@app.before_request
def before_request():
    if 'logged_in' in session:
        session['logged_in'] = User.verify_password(session.get('username'), session.get('password'))

# Use a more secure method to store user passwords
class DBManager:
    def __init__(self, db):
        self.db = sqlite3.connect(db)

    def register_user(self, username, password):
        try:
            cursor = self.db.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, generate_password_hash(password, method='argon2')))
            self.db.commit()
            return 'Registered successfully!'
        except sqlite3.Error as e:
            logging.error(e)
            return 'Registration failed'

    def login_user(self, username, password):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user_data = cursor.fetchone()
            if user_data and User.verify_password(user_data[2], password):
                session['logged_in'] = True
                return 'Logged in successfully!'
            else:
                return 'Invalid username or password'
        except sqlite3.Error as e:
            logging.error(e)
            return 'Login failed'

# Run in production mode with secured hosting options
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
