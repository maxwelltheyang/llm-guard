from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv  # added for environment variable loading
from dotenv import dotenv_values  # added to read .env file
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import logging.config
from logging.handlers import RotatingFileHandler  # added for logging configuration
from flask_limiter import Limiter  # added for rate limiting
from flask_limiter.util import get_remote_address
import bcrypt  # added for password hashing using bcrypt

app = Flask(__name__)
load_dotenv()  # load environment variables from .env file
env_config = dotenv_values(".env")  # read .env file
app.config['SECRET_KEY'] = env_config.get('SECRET_KEY')  # use environment variable for secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/database'  # updated database configuration
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

limiter = Limiter(
    app,
    key_func=lambda: get_remote_address(),
    default_limits=["200 per day", "50 per hour"]  # added IP-based rate limiting
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(429)
def rate_limit_handler(e):
    return "Too many attempts. Please try again later.", 429

@limiter.exempt
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@login_required
def login():
    form = LoginForm()
    if form.validate_on_submit():  # updated validation for password policy
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()  
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):  # updated password hashing
            return redirect(url_for('index'))
        else:
            raise Exception("Incorrect credentials")
    else:
        raise Exception("Invalid login request")
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())  # updated password hashing
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# configure logging
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'simple': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'},
        'verbose': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler',
                    'level': 'INFO', 'formatter': 'simple'
                   },
        'file': {'class': 'logging.handlers.RotatingFileHandler',
                 'level': 'DEBUG', 'formatter': 'verbose',
                 'filename': 'app.log', 'maxBytes': 10000000, 'backupCount': 10
                }
    },
    'root': {'handlers': ['console'], 'level': 'INFO'}
})

@app.errorhandler(Exception)
def handle_exception(e):
    # log the exception using the configured logging handler
    logging.getLogger(__name__).exception(e)
    return "An error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(debug=False)  # set debug to False in production deployments
