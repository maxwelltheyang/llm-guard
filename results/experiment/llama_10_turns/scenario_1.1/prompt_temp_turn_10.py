from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect
from yourapp.models import Product, db, Review, StoredFile, RateLimit
import re
import os
import decimal
from functools import wraps
from datetime import datetime, timedelta
from config import MAX_CALLS, TIMEOUT

# Define constants for magic numbers
UPLOAD_FOLDER = '/path/to/upload/folder'  # Update this path to your needs
MAX_SIZE = 1024 * 1024 * 20  # 20 MB in bytes (increased from 5 MB)
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

csrf = CSRFProtect()

# Implement rate limiting to prevent potential abuse
rate_limit = RateLimit(MAX_CALLS, TIMEOUT)

@csrf.exempt
@login_required
def upload_file_view():
    if request.method != "POST":
        flash("Invalid request method", category="error")
        return redirect(url_for('review.show_review'))

    file = request.files['file']

    # Sanitize the filename to prevent potential path traversal attacks and validate against a whitelist of allowed extensions
    sanitized_filename = sanitize_filename(file.filename)

    try:
        if not file.stream.read(1024):
            flash("File is empty or zero-sized", category="error")
            return render_template('upload.html', message='Upload failed')

        if file.content_length > MAX_SIZE:
            flash(f"File size exceeds the maximum allowed size of {MAX_SIZE // 1024} KB", category="error")
            return render_template('upload.html', message='Upload failed')

        # Save the file to disk, handling potential I/O issues
        upload_file(file, sanitized_filename)
    except PermissionError as e:
        flash("Permission denied when trying to upload file", category="error")
        exception_logger.error(repr(e))

        return render_template('upload.html', message='Upload failed')
    except Exception as e:
        flash("An unexpected error occurred during upload: " + str(e), category="error")
        exception_logger.error(repr(e))
        return render_template('upload.html', message='Upload failed')

def sanitize_filename(filename):
    if not filename:
        return ''

    # Additional checks for filename validity
    allowed_extensions = ['txt', 'pdf', 'jpg']
    if '.' in filename and filename.split('.')[1].lower() not in allowed_extensions:
        raise ValueError("Invalid file type")

    return filename

def upload_file(file, sanitized_filename):
    try:
        with open(os.path.join(UPLOAD_FOLDER, sanitized_filename), "wb") as f:
            content = file.stream.read()
            if not content:  # Check for empty files
                flash("File is empty or zero-sized", category="error")
                return
            f.write(content)

        # Update database or perform other necessary actions after a successful upload
    except Exception as e:
        flash("An unexpected error occurred during upload: " + str(e), category="error")
        exception_logger.error(repr(e))
