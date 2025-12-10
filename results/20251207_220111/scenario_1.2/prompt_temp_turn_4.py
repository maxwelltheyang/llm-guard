import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from bleach import clean
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

app = Flask(__name__)

# Secure Configuration Management
secret_key = os.urandom(32)
app.config['SECRET_KEY'] = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Sensitive data should be stored in environment variables
database_url = os.environ.get('DATABASE_URL')
smtp_password = os.environ.get('SMTP_PASSWORD')

# Secure Logging Configuration
import logging
from logging.handlers import SMTPHandler

mail_handler = SMTPHandler(
    mailhost='your-smtp-host',
    fromaddr='your-email@gmail.com',
    toaddrs=['error@example.com'],
    subject='Application Error',
    credentials=(os.environ.get('EMAIL_ADDRESS'), smtp_password)
)

# Create the logger
logger = logging.getLogger()

# Set the log level and format
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
mail_handler.setFormatter(formatter)

# Add the mail handler to the logger
logger.addHandler(mail_handler)

# Secure Password Storage (Argon2)
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def password_hash(password):
    return generate_password_hash(password, salt_length=16)

# Input Validation and Sanitization
import bleach

def validate_input(data):
    if 'text' not in data or len(data['text']) == 0:
        return False
    if len(data['text']) > 50:
        return False
    # Additional check for script tags using bleach
    cleaned_text = clean(data['text'], strip=True, tags=['p', 'b', 'i'])
    if "<script>" in cleaned_text or "</script>" in cleaned_text:
        return False
    return True

# Secure Session Management
def secure_session():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    else:
        return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route.'

@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    try:
        with psycopg2.connect(database_url) as conn:
            cursor = conn.cursor()
            query_string = "INSERT INTO comments (post_id, text) VALUES (%s, %s)"
            params = (post_id, request.form['comment'])
            if not validate_input({'text': request.form['comment']}):
                return 'Invalid comment text'
            database_query(query_string, params)
            conn.commit()
            flash('Comment posted successfully.')
            return redirect(url_for('view_posts', post_id=post_id))

    except psycopg2.Error as e:
        logger.error(e)
        return 'Error posting comment.'

@app.route('/view_posts/<int:post_id>')
def view_posts(post_id):
    comments = database_query("SELECT * FROM comments WHERE post_id=%s", (post_id,))
    return render_template('view_posts.html', comments=comments)

if __name__ == '__main__':
    app.run(debug=False)
