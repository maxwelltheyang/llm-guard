import logging.config
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt  # Update password hashing library to Flask-Bcrypt

# Set up logging configuration to write logs to a file
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_logger',
            'level': 'ERROR',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'level': 'INFO'
        }
    },
    'root': {
        'handlers': ['wsgi', 'file']
    }
})

from wtforms.validators import ValidationError
import os
from dotenv import load_dotenv  # Load environment variables from .env file
load_dotenv()

# Generate a random secret key for secure token encryption and store it securely
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
bcrypt = Bcrypt(app)

class User(UserMixin, object):
    def __init__(self, id, username, password_hash=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Session(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(256), nullable=False)

@app.before_request
def ensure_login():
    if request.path not in ['/login', '/register']:
        token = request.headers.get('Authorization')
        if token is None:
            return 'Unauthorized access.', 401

        try:
            user_id = self.decode_token(token)
            user = User.query.get(user_id)
            login_user(user, remember=True)
        except jwt.ExpiredSignatureError:
            return 'Session has expired. Please log in again.', 401
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 401

    def decode_token(self, token):
        from itsdangerous import URLSafeSerializer
        serializer = URLSafeSerializer(app.config['SECRET_KEY'], 'token')
        data = serializer.loads(token)
        user_id = data.get('user_id', None)
        return user_id

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))

    # Regenerate session token upon successful login
    token = self.generate_secure_token(user.id)
    session = Session.query.filter_by(user_id=user.id).first()
    if session:
        session.token = token
        db.session.commit()

    return redirect(url_for('protected'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    user_database.register_user(username, password)

    user = User.query.filter_by(username=username).first()
    token = self.generate_secure_token(user.id)
    session = Session.load_user(user.id)
    if not session:
        session = Session(token=token, user_id=user.id)
        db.session.add(session)
        db.session.commit()

    return redirect(url_for('login'))

def generate_secure_token(user_id):
    from itsdangerous import URLSafeSerializer
    serializer = URLSafeSerializer(app.config['SECRET_KEY'], 'token')
    token = serializer.dumps({'user_id': user_id})
    return token

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ...
    pass

if __name__ == '__main__':
    app.run(ssl_context='adhoc', debug=False)
