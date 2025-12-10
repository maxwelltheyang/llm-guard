from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import re
from passlib.context import CryptContext
import argparse
import secrets
import yaml

app = Flask(__name__)
bcrypt = CryptContext(schemes=["argon2"], default="argon2")
db = SQLAlchemy(app)

# Define secret key and other configuration variables in environment variables or secrets manager
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    logger.error("SECRET_KEY is not set")

DB_NAME = os.environ.get('DB_NAME')
if not DB_NAME:
    logger.error("DB_NAME is not set")

SECRETS_FILE_PATH = os.environ.get('SECRETS_FILE_PATH', '/path/to/secrets.yaml')
LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH', 'error.log')

# Check if environment variables exist before attempting to access them
try:
    with open(SECRETS_FILE_PATH, 'r') as f:
        secrets_data = yaml.safe_load(f)
except FileNotFoundError:
    logger.error("Secrets file not found")
    raise

# Hash and salt database password before storing it in memory
try:
    DB_PASSWORD_HASHED = bcrypt.hash(secrets_data['db_password'])
except KeyError:
    logger.error("DB password is not set in secrets file")
    raise

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(LOG_FILE_PATH)
handler.setFormatter(formatter)
logger.addHandler(handler)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

@app.errorhandler(500)
def internal_server_error(e):
    logger.exception('Internal Server Error occurred.')
    return render_template('error.html', error="An unexpected error occurred."), 500

# Search function to find blog posts by title or content
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        with db.session:
            results = BlogPost.query.filter(
                BlogPost.title.like(f'%{query}%') | BlogPost.content.like(f'%{query}%')
            ).all()
            return render_template('search_results.html', results=results)
    else:
        flash('Please enter a search query.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Disable Werkzeug debugger
    app.config['USE_RELOADER'] = False

    # Run application in production mode
    app.run(host='0.0.0.0', port=5000)
