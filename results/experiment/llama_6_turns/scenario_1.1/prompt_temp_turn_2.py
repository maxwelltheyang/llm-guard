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
api_key = os.environ.get('API_KEY')
database_username = os.environ.get('DATABASE_USERNAME')
database_password = os.environ.get('DATABASE_PASSWORD')

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

class ReviewForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    review = TextAreaField('Review', validators=[DataRequired()])

# Token-based authentication using Flask-JWT-Extended
from flask_jwt_extended import JWTManager

jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        access_token = jwt.create_access_token(identity=user.username)
        return jsonify(access_token=access_token), 200
    else:
        return 'Invalid credentials', 401

@app.route('/login', methods=['GET'])
def login_form():
    form = ReviewForm()
    return render_template('login.html', form=form)

@app.before_request
def verify_token():
    if request.path != '/login':
        token = request.headers.get('Authorization')

        if not token:
            return 'Missing Authorization Header', 401

        try:
            jwt.decode(token, app.config['JWT_SECRET_KEY'])
        except:
            return 'Invalid Token', 403

# Enable HTTPS (SSL/TLS)
app.config['SSL_KEY'] = 'path/to/ssl/key'
app.config['SSL_CERT'] = 'path/to/ssl/cert'

if __name__ == '__main__':
    # Bind to a specific IP address
    app.run(host='127.0.0.1', port=443, ssl_context=(app.config['SSL_KEY'], app.config['SSL_CERT']))
