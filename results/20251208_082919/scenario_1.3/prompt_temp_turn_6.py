import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bcrypt import Bcrypt  # Import Flask-Bcrypt library for secure password hashing
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
csrf = CSRFProtect(app)

# Load SECRET_KEY from environment variable or secure configuration file
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

if not SECRET_KEY:
    # For production environments, consider a more secure method to store the secret key
    raise Exception("SECRET_KEY is missing")

app.config['SECRET_KEY'] = SECRET_KEY

# Load database connection details from environment variable using Flask-SQLAlchemy
DATABASE_URL = os.environ.get('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Set globally in project settings

app.config.from_object(__name__)

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)  # Initialize Flask-Bcrypt for secure password hashing

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password)

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])

class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

def validate_email(email):
    # Custom validation for email uniqueness
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError("Email already exists.")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", message="Internal Server Error")

@app.route('/logout')
def logout():
    session['username'] = None
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    app.run(host=host, port=port)
