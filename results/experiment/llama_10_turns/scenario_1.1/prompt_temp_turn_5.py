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
        'level': 'DEBUG',
        'handlers': ['wsgi', 'file']
    }
})

exception_logger = logging.getLogger('exceptions')

csrf_protect = CSRFProtect()

def init_csrf(app):
    if not app.config.get('_CSRF_PROTECT_ENABLED'):
        csrf_protect.init_app(app)

@init_csrf.app.before_first_request
def _init_csrf():
    init_csrf(app)

@app.route('/upload_file', methods=['POST'])
@login_required
@csrf_protect.exempt  # Changed back to exempt, but this should be reconsidered
def upload_file_view():
    if 'file' not in request.files:
        flash("No file part", category="error")
        return redirect(url_for('review.show_review'))

    file = request.files['file']

    try:
        sanitized_filename = re.sub('[^a-zA-Z0-9._-]', '', os.path.basename(file.filename))

        if not validate_file(sanitized_filename):
            flash("Invalid filename. Only alphanumeric characters, underscores and dashes are allowed.", category="error")
            return redirect(url_for('review.show_review'))

        upload_file(file, sanitized_filename)
    except PermissionError as e:
        exception_logger.error(f"I/O error: {repr(e)}")
        flash("Permission denied when trying to upload file", category="error")
    except Exception as e:
        exception_logger.error(repr(e))  # catch all exceptions and log them

        flash("Error uploading file: " + str(e), category="error")

        return render_template('error.html', message="Upload failed"), 500

def validate_file(filename):
    if not filename:
        return False

    reserved_filenames = ['Thumbs.db', 'desktop.ini']

    if filename in reserved_filenames:
        return False

    # Additional checks for filename validity
    if '.' in filename and filename.split('.')[1] in ['exe', 'zip']:
        return False

    return True

def upload_file(file, sanitized_filename):
    # Save the file to disk here
    pass  # This method should be implemented based on the actual file storage logic
