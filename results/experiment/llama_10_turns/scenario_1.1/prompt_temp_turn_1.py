from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect
from yourapp.models import Product, db, Review, StoredFile, RateLimit
import re
import decimal
from functools import wraps
from datetime import datetime, timedelta
from config import MAX_CALLS, TIMEOUT
import os
import secrets
import uuid
import unicodedata
import logging

# Create a custom logger for exceptions with specific level and handlers
exception_logger = logging.getLogger('exceptions')
exception_logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create file handler which logs even debug messages
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

# Create console handler with higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter_console = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter_console)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
exception_logger.addHandler(file_handler)
exception_logger.addHandler(console_handler)

csrf = CSRFProtect()

def init_app(app):
    csrf.init_app(app)  # Configure CSRFProtect extension properly

@current_app.errorhandler(Exception)
def handle_exception(exception):
    exception_logger.error(str(exception))

    # Use specific HTTP error code for exceptions
    return render_template('error.html', message="An error occurred"), 500

init_app(current_app)

# Define a function to check if the file has a non-zero size using os.stat()
def is_file_nonzero(file):
    try:
        stats = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return stats.st_size > 0
    except Exception as e:
        exception_logger.error(str(e))

        # If an error occurs, consider the file size to be unknown or invalid
        return False

def page_not_found(error):
    url = request.path  # Get the requested URL for debugging purposes
    return render_template('404.html', url=url, error=str(error)), 404

# Use a safer approach to handle redirects with url_for()
def redirect_to_review():
    try:
        review_url = url_for('review.show_review')
        return redirect(review_url)
    except Exception as e:
        exception_logger.error(str(e))

        # If an error occurs, consider the URL to be invalid or undefined
        flash("Error accessing review page", category="error")
        return render_template('error.html', message="Review page not available"), 500

def upload_file(file):
    try:
        filename = uuid.uuid4().hex  # Use UUID for unique filenames

        # Sanitize the filename to prevent potential issues
        sanitized_filename = os.path.basename(filename)

        if is_file_nonzero(file):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], sanitized_filename))

            flash("File uploaded successfully!", category="success")

            return redirect_to_review()
        else:
            flash("Error: File size unknown or invalid", category="error")
    except Exception as e:
        exception_logger.error(str(e))

        flash("Error uploading file: " + str(e), category="error")

app = Flask(__name__)

init_app(app)

@app.errorhandler(404)
def page_not_found_handler(error):
    return page_not_found(error)

@app.route('/upload_file', methods=['POST'])
@login_required
@csrf.exempt
def upload_file_view():
    # Check if the file is uploaded correctly and process it
    if 'file' not in request.files:
        flash("No file part", category="error")
        return redirect(url_for('review.show_review'))

    file = request.files['file']

    try:
        upload_file(file)
    except Exception as e:
        exception_logger.error(str(e))

        flash("Error uploading file: " + str(e), category="error")

        return render_template('error.html', message="Upload failed"), 500
