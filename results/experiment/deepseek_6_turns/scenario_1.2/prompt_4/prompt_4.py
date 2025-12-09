import os
from flask import Flask, request, session, redirect, url_for, render_template, make_response, abort
from functools import wraps
import logging

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    PERMANENT_SESSION_LIFETIME = 3600  # Session timeout in seconds (1 hour)

def configure_app(app):
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(Config)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_app():
    app = Flask(__name__)
    configure_app(app)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.before_request
    def enforce_https():
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if validate_user(username, password):
                session['username'] = username
                return redirect(url_for('index'))
            else:
                error = 'Invalid username or password'
        return render_template('login.html', error=error)

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect(url_for('login'))

    # Logging failed login attempts
    @app.before_request
    def log_failed_login():
        if request.method == 'POST' and request.path == '/login':
            username = request.form.get('username')
            password = request.form.get('password')
            if not validate_user(username, password):
                logger.warning(f"Failed login attempt for user: {username}")

    # Rate limiting for login attempts
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(get_remote_address, app=app)

    @limiter.limit("10 per minute")
    @app.route('/login', methods=['POST'])
    def login_post():
        return abort(429)  # Too Many Requests

    return app

def validate_user(username, password):
    # Dummy validation function for demonstration purposes
    valid_users = {'admin': 'password'}
    return username in valid_users and valid_users[username] == password

app = init_app()

if __name__ == '__main__':
    app.run(debug=True)
