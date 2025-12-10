import os
from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from argon2 import PasswordHasher
from wtforms import Form, StringField, IntegerField, validators
import re
import pathlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
DEBUG = os.environ.get('FLASK_DEBUG', False)
if not DEBUG:
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    app.config['WTF_CSRF_ENABLED'] = True  # Re-enabled CSRF protection for production environments
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

db = SQLAlchemy(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def get_remote_address():
    return request.remote_addr

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.String(64))

def register_user(username, password):
    try:
        user = User.query.filter_by(username=username).first()

        if user:
            return False

        hashed_password = PasswordHasher().hash(password)

        user = User(username=username, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        return True

    except Exception as e:
        print(f"Error registering user: {e}")
        return False

class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')

class RegistrationForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5/hour")
def register():
    form = RegistrationForm()

    if request.method == 'POST' and form.validate():
        hashed_password = PasswordHasher().hash(form.password.data)

        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error committing session: {e}")
            return 'Registration failed', 400

        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error logging out user: {e}")
        return 'Logout failed', 400

if __name__ == '__main__':
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0')
