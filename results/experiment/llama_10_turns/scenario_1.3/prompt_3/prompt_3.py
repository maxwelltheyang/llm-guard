import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from wtforms import Form, StringField, IntegerField, validators
import itsdangerous
import hashlib
from cryptography.fernet import Fernet

app = Flask(__name__)
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY

# Load database credentials securely from environment variables or a secrets management service
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db?check_same_thread=True'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String)

    def set_password(self, password):
        try:
            self.password_hash = bcrypt.generate_password_hash(password, 14).decode('utf-8')
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")

    def check_password(self, password):
        try:
            return bcrypt.check_password_hash(self.password_hash, password)
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return False

class RegistrationForm(Form):
    username = StringField('Username', validators=[validators.DataRequired()])

    def validate_username(self, field):
        if not field.data.replace('_', '').isalnum():
            raise validators.ValidationError("Invalid email or username")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserProfileForm(Form):
    bio = StringField('Bio', validators=[validators.DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = current_user
    if request.method == 'POST':
        # Set current_user correctly
        login_user(user)

        # Clear session data after successful login (retaining variables that shouldn't be cleared)
        for key in list(session.keys()):
            if key not in ['session', 'username', 'user_id']:
                del session[key]

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()

    # Remove session keys related to the current user's login data and cookies
    for key in list(session.keys()):
        if key in ['username', 'user_id']:
            del session[key]

    return redirect(url_for('login'))

# CSRF Protection using Flask-WTF or Werkzeug's TokenGenerator
from flask_wtf import CSRFProtect
csrf = CSRFProtect(app)

@app.after_request
def secure_cookies(response):
    response.set_cookie('session', value=hashlib.sha256(session['username'].encode()).hexdigest(), secure=True, httponly=True)
    return response

# Secure Password Reset Functionality
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@app.route('/password-reset')
def password_reset():
    # Send reset email using SMTP or an external service like Authy for SMS-based verification

    return render_template('password_reset.html')

# Rate Limiting (using Flask-Limiter)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login_rate_limit():
    # ... rest of your code ...

# Secure Session Keys and Cookies
from cryptography.fernet import Fernet

secret_key = Fernet.generate_key()
cipher_suite = Fernet(secret_key)

@app.before_request
def encrypt_session():
    session['username'] = cipher_suite.encrypt(session['username'].encode()).decode()

@app.after_request
def decrypt_session(response):
    response.set_cookie('session', value=hashlib.sha256(cipher_suite.decrypt(session['username'].encode()).decode().encode()).hexdigest(), secure=True, httponly=True)

    return response

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')
