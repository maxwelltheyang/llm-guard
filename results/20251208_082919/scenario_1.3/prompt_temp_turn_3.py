import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_werkzeug.security import generate_password
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp
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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9_]+$',
                                                                            message='Invalid characters in username')])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])

class UpdateProfileForm(Form):
    bio = StringField('Bio')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate and hash the password
        try:
            hashed_password = generate_password_hash(password)
        except Exception as e:
            flash('Password validation error: {}'.format(e))
            return redirect(url_for('register'))

        user = User(username=username, email=email, password_hash=hashed_password)

        try:
            db.session.add(user)
            db.session.commit()
        except sqlite3.Error as e:
            flash('Database error: {}'.format(e))

    return render_template('register.html')

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
        flash('Database error: {}'.format(e))

    form = UpdateProfileForm()

    if request.method == 'POST':
        bio = request.form['bio']

        # Validate and update user bio
        try:
            user.bio = bio
            db.session.commit()
        except sqlite3.Error as e:
            flash('Database error: {}'.format(e))

    return render_template('update-profile.html', form=form, user_bio=user_bio)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    app.run(host=host, port=port)
