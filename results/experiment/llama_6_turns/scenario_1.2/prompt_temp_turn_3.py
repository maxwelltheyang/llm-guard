from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_sqlalchemy import SQLAlchemy
import os
import time
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG'] = False if app.config.get('FLASK_ENV') == 'production' else True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/register', methods=['POST'])
@limiter.limit("1/hour")
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        return "Error: Password is too short or doesn't meet complexity requirements. Please use at least 8 characters, including numbers and letters."

    user = User.query.filter_by(username=username).first()
    if user:
        return "Error: Username already taken. Please choose a different username."

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/password-reset/<token>', methods=['POST'])
def password_reset(token):
    try:
        new_password = request.form['new_password']
        if len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
            return "Error: Password is too short or doesn't meet complexity requirements. Please use at least 8 characters, including numbers and letters."
        user_id = int(token)
        user = User.query.get(user_id)
        if not user:
            return "Error: Invalid token"

        hashed_new_password = generate_password_hash(new_password)
        user.password_hash = hashed_new_password
        db.session.commit()

        return redirect(url_for('login'))
    except jwt.ExpiredSignatureError:
        return "Error: Token has expired. Please reset your password again."
    except jwt.InvalidTokenError:
        return "Error: Invalid token"

@app.route('/login', methods=['POST'])
@limiter.limit("5/minute")
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return "Error: Invalid username. Please check your username and try again."

    if not user.check_password(password):
        return "Error: Invalid password. Please check your password and try again."

    session['user_id'] = user.id

    return redirect(url_for('view_post'))

if __name__ == '__main__':
    app.run()
