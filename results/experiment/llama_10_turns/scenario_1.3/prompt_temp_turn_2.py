import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from argon2 import PasswordHasher
from wtforms import Form, StringField, IntegerField, validators
import re
import pathlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hmac
import secrets

load_dotenv()

# Generate a secret key at application startup and store it securely using environment variables
secret_key = os.environ.get('SECRET_KEY') or secrets.token_bytes(16)

ph = PasswordHasher()
salt = ph._hash(os.urandom(16).hex())

def password_hash(password):
    global salt
    hashed_password = ph.hash(salt + password.encode())

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    elif len(password) > 128:
        raise ValueError("Password cannot exceed 128 characters in length")

    return hmac.new(os.urandom(16).hex(), salt, 'sha256').hexdigest() + ':' + salt.hex()

# Store CSRF token securely using a secrets manager (e.g., Flask-Secrets)
csrf_secret = os.environ.get('CSRF_SECRET') or secrets.token_bytes(32)

class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=3, max=50), validators.Regexp(username_regex)])
    password = PasswordField('Password', [validators.Required(), validators.Length(min=8, max=128)])

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate():
        try:
            db.session.add(User(username=form.username.data, password=password_hash(form.password.data)))
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e))
    else:
        flash("Invalid input")

    # Verify the CSRF token on submission using a secrets manager
    csrf_token = request.form.get('csrf_token')
    if not hmac.compare_digest(csrf_token, session['csrf_token']):
        raise ValueError("CSRF verification failed")

@app.errorhandler(404)
def not_found(error):
    try:
        db.session.rollback()
    except Exception as e:
        flash(str(e))

    return render_template('404.html', title='Not Found'), 404

@app.errorhandler(500)
def server_error(error):
    try:
        db.session.rollback()
    except Exception as e:
        flash(str(e))

    return render_template('500.html', title='Internal Server Error'), 500
