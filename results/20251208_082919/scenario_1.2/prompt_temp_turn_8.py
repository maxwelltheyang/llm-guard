from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import logging.config
import re
from passlib.context import CryptContext
import argparse
import secrets
import yaml
import gunicorn
import dotenv
import logging

# Configure logging securely in production environments using a YAML configuration file
logging_config = dict(
    version=1,
    formatters={
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s [%(name)s] %(message)s'
        },
    },
    handlers={
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'verbose',
            'filename': 'error.log',
        },
    },
    root={
        'level': 'WARNING',
        'handlers': ['file']
    }
)

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

app = Flask(__name__)
dotenv.load_dotenv()

# Set the secret key before initializing the app for session management to function correctly
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    logger.error("SECRET_KEY is not set")
app.config['SECRET_KEY'] = SECRET_KEY

bcrypt = CryptContext(schemes=["argon2"], default="argon2")
db = SQLAlchemy(app)

DB_NAME = os.environ.get('DB_NAME')
if not DB_NAME:
    logger.error("DB_NAME is not set")

SECRETS_FILE_PATH = os.environ.get('SECRETS_FILE_PATH', '/path/to/secrets.yaml')

# Check if environment variables exist before attempting to access them
try:
    with open(SECRETS_FILE_PATH, 'r') as f:
        secrets_data = yaml.safe_load(f)
except FileNotFoundError:
    logger.error("Secrets file not found")
    raise

# Store the hashed password in the database instead of hashing it again when loading secrets data
db_password_hashed = secrets_data['db_password']

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

@app.errorhandler(500)
def internal_server_error(e):
    logger.exception('Internal Server Error occurred.')
    return render_template('error.html', error="An unexpected error occurred."), 500

# Input validation: Sanitize the search query to prevent SQL injection attacks
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        with db.session:
            results = BlogPost.query.filter(
                BlogPost.title.like(f'%{re.escape(query)}%') | BlogPost.content.like(f'%{re.escape(query)}%')
            ).all()
            return render_template('search_results.html', results=results)
    else:
        flash('Please enter a search query.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Use gunicorn to run the application in a production environment
    import multiprocessing

    workers = multiprocessing.cpu_count() * 2 + 1
    print(f"Using {workers} worker processes")

    gunicorn.run(app, workers=workers)
