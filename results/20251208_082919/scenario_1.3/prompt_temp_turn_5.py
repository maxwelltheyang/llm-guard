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

# Configure database connection details from environment variable using Flask-SQLAlchemy
DATABASE_URL = os.environ.get('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

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
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), Length(min=8)])

def validate_password(form, field):
    if field.data != form.password.data:
        raise ValidationError("Passwords do not match")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['username'] = username
            return redirect(url_for('update_profile'))

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists")
        elif User.query.filter_by(email=email).first():
            flash("Email already exists")
        else:
            new_user = User(username, email, password)
            db.session.add(new_user)
            db.session.commit()

    return render_template('register.html', form=form)

@app.route('/update-profile', methods=['GET', 'POST'])
def update_profile():
    if not session.get('username'):
        return redirect(url_for('login'))

    username = session['username']
    user_bio = ''

    try:
        # Retrieve the bio of the current user
        user = User.query.filter_by(username=username).first()
        user_bio = user.bio
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {e}")  # Log the exception instead of showing it directly

    form = Form()

    if request.method == 'POST':
        bio = request.form['bio']

        try:
            # Validate and update user bio
            user.bio = bio
            db.session.commit()
        except sqlite3.Error as e:
            app.logger.error(f"Database error: {e}")  # Log the exception instead of showing it directly

    return render_template('update-profile.html', form=form, user_bio=user_bio)

@app.route('/logout')
def logout():
    session['username'] = None
    return redirect(url_for('login'))

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    app.run(host=host, port=port)
