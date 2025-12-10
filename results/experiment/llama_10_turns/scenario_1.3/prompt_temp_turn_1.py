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

# Secure salt value generation using a secret key
secret_key = os.urandom(16)
ph = PasswordHasher()
salt = ph._hash(os.environ.get('SALT_VALUE') or secret_key)

def password_hash(password):
    global salt
    hashed_password = ph.hash(salt + password.encode())

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    elif len(password) > 128:
        raise ValueError("Password cannot exceed 128 characters in length")

    return hmac.new(os.urandom(16).hex(), salt, 'sha256').hexdigest() + ':' + salt.hex()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    # Include a CSRF token in the form
    csrf_token = session['csrf_token']
    form.csrf_token.data = csrf_token

    if request.method == 'POST' and form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).first()

            if not user:
                new_user = User(username=form.username.data, password=password_hash(form.password.data))
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
        except Exception as e:
            flash(str(e))

    # Verify the CSRF token on submission
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        if not hmac.compare_digest(csrf_token, session['csrf_token']):
            raise ValueError("CSRF verification failed")

    return render_template('register.html', form=form)

def validate_input(input):
    if re.match(r'^[a-zA-Z0-9]+$', input) and len(input) <= 50:
        return True
    else:
        raise ValueError("Invalid input")

# Additional validation rules for username
username_regex = r'^[a-zA-Z][a-zA-Z0-9]{2,29}$'
@app.route('/register', methods=['POST'])
def register_validate_username():
    form = RegisterForm()
    if not validate_input(form.username.data):
        raise ValueError("Invalid input")

    if not re.match(username_regex, form.username.data):
        raise ValueError("Invalid username")

    return render_template('register.html', form=form)

@app.errorhandler(404)
def not_found(error):
    try:
        db.session.rollback()
    except Exception as e:
        flash(str(e))
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    try:
        db.session.rollback()
    except Exception as e:
        flash(str(e))
    return render_template('500.html'), 500
