from flask import Flask, render_template, request, redirect, url_for, flash, session
from logging.config import dictConfig
import os
from wtforms import Form, StringField, FloatField, validators, PasswordField
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from passlib.context import CryptContext

# Set up logging configuration
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_logger',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    logging.error("SECRET_KEY not set. Aborting startup.")
    raise RuntimeError('SECRET_KEY must be set')

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTP_ONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_PERMANENT'] = False

from flask_session import Session
Session(app)

app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get('CSRF_SECRET', 'default_secret')

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username, email, password):
        self.id = username
        self.username = username
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(username):
    user = User.query.filter_by(username=username).first()
    return user if user else None

class LoginForm(Form):
    username = StringField(validators=[validators.required()])
    password = PasswordField(validators=[validators.required()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        pwd_context = CryptContext(schemes=["argon2id"], default="argon2id")
        if user and pwd_context.verify(password, user.password):
            login_user(user)
            flash('Logged in successfully')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', category='error')

    return render_template('login.html', form=form)

class RegisterForm(Form):
    username = StringField(validators=[validators.required()])
    email = StringField(validators=[validators.required(), validators.Email()])
    password = PasswordField(validators=[validators.required()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User(username, email, pwd_context.hash(password))
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Registration successful. Login to continue.')
        return redirect(url_for('home'))

    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)
