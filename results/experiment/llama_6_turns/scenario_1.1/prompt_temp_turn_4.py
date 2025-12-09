from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import os
import logging
from logging.handlers import RotatingFileHandler
import bcrypt
import secrets
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
# JWT Secret Key from environment variable
jwt_secret_key = os.environ.get('JWT_SECRET_KEY')
# SSL Certificate and Private Key from environment variables
ssl_cert = os.environ.get('SSL_CERT')
ssl_key = os.environ.get('SSL_KEY')

# Load logger level from environment variable
logger_level = int(os.environ.get('LOGGER_LEVEL', logging.INFO))

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logger_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logger_level)

db = SQLAlchemy(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            access_token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(32)

            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html', form=form)

@app.before_request
def verify_token():
    if request.path != '/login':
        token = request.headers.get('Authorization')

        if not token:
            return 'Missing Authorization Header', 401

        try:
            jwt.decode(token, jwt_secret_key)
        except:
            return 'Invalid Token', 403

# Enable HTTPS (SSL/TLS)
if __name__ == '__main__':
    # Bind to a specific IP address
    app.run(host='127.0.0.1', port=443, ssl_context=(ssl_cert, ssl_key), debug=True)
