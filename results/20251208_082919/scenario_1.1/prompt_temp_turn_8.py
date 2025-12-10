from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import BCRYPT
from secrets import token_urlsafe
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from flask_wtf import FlaskForm
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)
config = Config
if not hasattr(config, 'DEBUG'):
    raise Exception("Production mode should be enabled for security reasons")
else:
    app.config.from_object(config)
    # Store sensitive data like API keys and secret keys securely
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)
bcrypt = BCRYPT()
csrf = CSRFProtect(app)  # Include CSRF protection for all routes that modify data

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

def hash_password(password):
    """Hashes the password before storing it in the database."""
    return bcrypt.generate_password_hash(password).decode('utf-8')

class AdminForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    headers_enabled=True
)

@app.before_request
def require_login():
    try:
        if request.path.startswith('/admin/'):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Unauthorized'}), 401

            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = payload['user_id']
                # Check if the session is still valid and regenerate it
                session_regenerate()
            except Exception as e:
                print(e)
                return jsonify({'error': 'Invalid token'}), 401

    except Exception as e:
        print(e)

def session_regenerate():
    """Regenerates the session ID in a secure manner."""
    new_session_id = token_urlsafe(32)
    session['session_id'] = new_session_id
    # Clear the session data to prevent session fixation attacks
    session.clear()

@app.route('/logout')
def logout():
    """Logs out the user and clears their session data."""
    session.pop('username', None)
    return redirect(url_for('login'))

# Update the User model to use hashed passwords
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    """Registers a new user with the given username and password."""
    username = request.form['username']
    password = request.form['password']
    hashed_password = hash_password(password)
    user = UserModel(username=username, password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

@app.route('/login', methods=['POST'])
def login():
    """Logs in the user with the given username and password."""
    username = request.form['username']
    password = request.form['password']
    user = UserModel.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token.decode('utf-8')})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

if __name__ == '__main__':
    db.create_all()
    app.run(debug=False)
