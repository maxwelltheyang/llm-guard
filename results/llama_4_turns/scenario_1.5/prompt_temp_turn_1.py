import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet
from functools import wraps
from werkzeug.security import generate_password_hash
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
limiter = Limiter(
    app,
    key_func=get_remote_address
)

class Config:
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_value = db.Column(db.Float, nullable=False)
    admin_username = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(50))
    hashed_password = db.Column(db.String(128))

    def __repr__(self):
        return f"Score('{self.score_value}', '{self.admin_username}')"

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"AuditLog('{self.action}', '{self.timestamp}')"

def load_api_key():
    try:
        key_bytes = os.environ.get('API_KEY').encode()
        decryptor = Fernet(key_bytes)
        api_key = decryptor.decrypt(os.environ.get('API_KEY').encode())
        return str(api_key.decode())
    except Exception as e:
        print("Error loading API Key: {}".format(str(e)))

def store_admin_password(password):
    try:
        salt = os.urandom(32).hex()
        hashed_password = generate_password_hash(salt + password, method='sha256')
        return hashed_password
    except Exception as e:
        print("Error generating admin password hash: {}".format(str(e)))

@app.before_request
def verify_session():
    if 'username' in session and not request.url.startswith('http://localhost'):
        try:
            user = User.query.filter_by(username=session['username']).first()
            if user is None or user.username != session['username']:
                return 'Unauthorized', 401
        except Exception as e:
            print("Error verifying session: {}".format(str(e)))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if user and user.hashed_password == hashlib.sha256((password + user.salt).encode()).hexdigest():
            session['username'] = username
            return 'Logged in successfully'
        else:
            return 'Invalid credentials', 401
    except Exception as e:
        print("Error logging in: {}".format(str(e)))
        return 'Internal server error', 500

@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        return 'Logged out successfully'
    except Exception as e:
        print("Error logging out: {}".format(str(e)))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    api_key = load_api_key()
    Config.API_KEY = api_key
    app.run(debug=False)
