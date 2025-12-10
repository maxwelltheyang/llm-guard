import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from bleach import clean
from pg8000 import postgresql as pg
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import flask_limiter
from argon2 import PasswordHasher

app = Flask(__name__)

# Secure Configuration Management
secret_key = os.urandom(32)
app.config['SECRET_KEY'] = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

database_url = os.environ.get('DATABASE_URL')
smtp_password = os.environ.get('SMTP_PASSWORD')
smtp_host = os.environ.get('SMTP_HOST')
smtp_user = os.environ.get('SMTP_USER')

# Sensitive data should be stored in environment variables
email_address = os.environ.get('EMAIL_ADDRESS')

# Secure Logging Configuration
import logging
from logging.handlers import SMTPHandler

mail_handler = SMTPHandler(
    mailhost=smtp_host,
    fromaddr=email_address,
    toaddrs=['error@example.com'],
    subject='Application Error',
    credentials=(os.environ.get('SMTP_USER'), smtp_password)
)

logger = logging.getLogger()
logger.addHandler(mail_handler)

# Secure Database Connection
def database_query(query_string, params):
    try:
        with pg.connect(database_url) as conn:
            cursor = conn.cursor()
            cursor.execute(query_string, params)
            return cursor.fetchall()
    except Exception as e:
        logger.error(e)
        flash('Error occurred while connecting to the database.')

# Secure Password Hashing
ph = PasswordHasher()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route.'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            try:
                return redirect(url_for('login'))
            except Exception as e:
                logger.error(e)
                flash('An error occurred while handling the login request.')
                return render_template('login.html')
        return f(*args, **kwargs)
    return decorated_function

# Rate limiting for login attempts
limiter = flask_limiter.Limiter(app, key_func=get_remote_address)

@app.route('/comment/<int:post_id>', methods=['POST'])
@limiter.limit("10/minute")  # Limit login attempts to 10 per minute
def comment(post_id):
    try:
        with pg.connect(database_url) as conn:
            cursor = conn.cursor()
            query_string = "INSERT INTO comments (post_id, text) VALUES (%s, %s)"
            params = (post_id, request.form['comment'])
            if not validate_input({'text': request.form['comment']}):
                return 'Invalid comment text'
            database_query(query_string, params)
            conn.commit()
            flash('Comment posted successfully.')
            return redirect(url_for('view_posts', post_id=post_id))

    except Exception as e:
        logger.error(e)
        flash('Error posting comment.')

@app.route('/view_posts/<int:post_id>')
def view_posts(post_id):
    comments = database_query("SELECT * FROM comments WHERE post_id=%s", (post_id,))
    return render_template('view_posts.html', comments=comments)

# Secure password verification
@app.route('/login', methods=['POST'])
@limiter.limit("10/minute")  # Limit login attempts to 10 per minute
def login():
    username = request.form['username']
    password = request.form['password']

    if not validate_input({'username': username, 'password': password}):
        return 'Invalid input'

    try:
        user_data = database_query("SELECT * FROM users WHERE username=%s", (username,))
        if len(user_data) == 0 or not ph.verify(user_data[0][1], password):
            flash('Incorrect username or password.')
            return render_template('login.html')
        session['logged_in'] = True
        return redirect(url_for('protected'))
    except Exception as e:
        logger.error(e)
        flash('An error occurred while handling the login request.')
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=False)
