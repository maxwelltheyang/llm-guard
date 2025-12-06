from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv  # added for environment variable loading
from dotenv import dotenv_values  # added to read .env file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
load_dotenv()  # load environment variables from .env file

# database configuration
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# secret key management
SECRET_KEY = os.getenv('SECRET_KEY')

# configure logging
import logging.config

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

# password policy validation
def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    if not any(char.isalpha() for char in password):
        raise ValueError("Password must contain at least one letter")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            validate_password(password)
            hashed_password = generate_password_hash(password, method='sha256')
            db.session.add(User(username=username, password=hashed_password))
            db.session.commit()
            return redirect(url_for('login'))
        except ValueError as e:
            return render_template('register.html', error=e)
    return render_template('register.html')

# login attempts limit
failed_login_attempts = {}

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # 5 attempts per minute
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if check_password_hash(user.password, password):
                return redirect(url_for('index'))
            else:
                failed_login_attempts[request.remote_addr] = (failed_login_attempts.get(request.remote_addr, 0) + 1)
                logging.warning(f"Failed login attempt from {request.remote_addr}")
                if failed_login_attempts[request.remote_addr] >= 5:
                    logging.info(f"Banning IP address {request.remote_addr} due to excessive failed login attempts")
                    limiter.limit("10 per hour")(index)  # temporarily ban IP address for an hour
        except Exception as e:
            logging.error(e)
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=False)  # set debug to False in production deployments
