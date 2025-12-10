from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect
from yourapp.models import Product, db, Review, StoredFile, RateLimit
import re
import decimal
from functools import wraps
from datetime import datetime, timedelta
from config import MAX_CALLS, TIMEOUT

# Define constants for magic numbers
UPLOAD_FOLDER = '/path/to/upload/folder'  # Update this path to your needs
MAX_SIZE = 1024 * 1024 * 5  # 5 MB in bytes
TIMEOUT_SECONDS = 60  # 1 minute in seconds

# Create a custom logger for exceptions with specific level and handlers
import logging.config
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})

# CSRFProtect extension initialization
csrf = CSRFProtect()

def init_app(app):
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # store secret key securely
    csrf.init_app(app)

from flask import current_app

init_app(app)

@app.before_request
def check_csrf_token():
    if request.method == 'POST':
        token = request.form['csrf_token']
        if not token or token != get_csrf_token():
            return "Invalid CSRF token", 400

def get_csrf_token():
    return current_app.config.get('SECRET_KEY')

@app.errorhandler(500)
def internal_server_error(e):
    exception_logger.error(repr(e))

    # additional logging for I/O-related exceptions
    if isinstance(e, PermissionError) or isinstance(e, IOError):
        exception_logger.error(f"I/O error: {repr(e)}")

    return render_template('error.html', message="Internal Server Error"), 500

@app.route('/upload_file', methods=['POST'])
@login_required
@csrf.exempt
def upload_file_view():
    if 'file' not in request.files:
        flash("No file part", category="error")
        return redirect(url_for('review.show_review'))

    file = request.files['file']

    try:
        # Sanitize the filename using a more robust approach (e.g., only allow alphanumeric characters, underscores, and dashes)
        sanitized_filename = re.sub('[^a-zA-Z0-9._-]', '', os.path.basename(file.filename))

        if not validate_file(sanitized_filename):
            return render_template('error.html', message="Invalid file name")

        upload_file(file, sanitized_filename)  
    except Exception as e:
        exception_logger.error(repr(e))  # catch all exceptions and log them

        flash("Error uploading file: " + str(e), category="error")

        return render_template('error.html', message="Upload failed"), 500

def validate_file(filename):
    # Check if the filename is not empty
    if not filename:
        return False

    # Additional checks for filename validity (e.g., check for reserved filenames)
    if filename in ['Thumbs.db', 'desktop.ini']:
        return False

    return True
