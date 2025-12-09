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
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG'] = False if app.config.get('FLASK_ENV') == 'production' else True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['WTF_CSRF_TIME_LIMIT'] = 300

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

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password', render_kw={'placeholder': 'Minimum 8 characters, including numbers and letters'})
    submit = SubmitField('Login')

@app.route('/register', methods=['POST'])
@limiter.limit("1/hour")
def register():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()
            if not user:
                new_user = User(username=username, email=request.form['email'], password_hash=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('login'))
            else:
                return "Error: Username already exists. Please choose a different username."
        else:
            return "Form is invalid"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/login', methods=['POST'])
@limiter.limit("5/minute")
def login():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()
            if not user:
                return "Error: Invalid username. Please check your username and try again."

            if not user.check_password(password):
                return "Error: Invalid password. Please check your password and try again."

            session['user_id'] = user.id

            return redirect(url_for('view_post'))
        else:
            return "Form is invalid"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            token = secrets.token_urlsafe(16)
            user_id = request.form['user_id']
            user = User.query.get(user_id)
            user.reset_token = token
            db.session.commit()

            return redirect(url_for('view_post'))
        else:
            return "Form is invalid"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/reset-password-confirm', methods=['POST'])
def reset_password_confirm():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            token = request.form['token']
            password = request.form['password']

            user_id = int(token)
            user = User.query.get(user_id)
            if not user:
                return "Error: Invalid token"
            elif user.reset_token != token:
                return "Error: Token has expired. Please reset your password again."
            else:
                hashed_new_password = generate_password_hash(password)
                user.password_hash = hashed_new_password
                db.session.commit()

                return redirect(url_for('login'))
        else:
            return "Form is invalid"
    except jwt.ExpiredSignatureError:
        return "Error: Token has expired. Please reset your password again."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run()
