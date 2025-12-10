import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from passlib.hash import argon2
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

ph = argon2

class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=3, max=50), validators.Regexp(username_regex)])
    password = PasswordField('Password', [validators.Required(), validators.Length(min=8, max=128)])

# Create a secret for CSRF token verification
csrf_secret = secrets.token_bytes(16)

def verify_csrf_token():
    csrf_token = request.form.get('csrf_token')
    if not hmac.compare_digest(csrf_token, session['csrf_token']):
        raise ValueError("CSRF verification failed")

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate():
        try:
            verify_csrf_token()
            db.session.add(User(username=form.username.data, password=ph.hash(form.password.data)))
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e))
    else:
        flash("Invalid input")

    # Return the CSRF token
    session['csrf_token'] = secrets.token_hex(16)
    return render_template('register.html')

@app.route('/sanitize_session')
def sanitize_session():
    try:
        for key, value in list(session.items()):
            if 'password' in key or 'token' in key:
                del session[key]
    except Exception as e:
        flash(str(e))

    return 'Session sanitized'

# Log sensitive data securely
import logging
logger = logging.getLogger(__name__)
try:
    with open('sensitive_data.log', 'a') as f:
        logger.addHandler(logging.FileHandler(f, mode='w'))
except Exception as e:
    flash(str(e))

@app.before_first_request
def update_dependencies():
    try:
        import pip
        from pip import main as pip_main
        pip_main(['install', '--upgrade', 'pip'])
        pip_main(['install', '--upgrade', 'flask'])
        pip_main(['install', '--upgrade', 'passlib'])
    except Exception as e:
        flash(str(e))

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

# IP blocking
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
@app.after_request
def log_after_request(response):
    try:
        db.session.commit()
    except Exception as e:
        flash(str(e))

    return response

# Rate limiting
@limiter.exempt
@login_required
def protected():
    pass

# Additional logging for suspicious activity
if __name__ == "__main__":
    import logging.config
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'}
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'level': 'DEBUG',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    })
