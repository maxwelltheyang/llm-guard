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
    exception_logger.error(repr(exception))  # Use repr() for safer string construction

    # Use specific HTTP error code for exceptions
    return render_template('error.html', message="An error occurred"), 500

@app.route('/upload_file', methods=['POST'])
@login_required
@csrf.exempt
def upload_file_view():
    if 'file' not in request.files:
        flash("No file part", category="error")
        return redirect(url_for('review.show_review'))

    file = request.files['file']

    try:
        # Sanitize the filename to prevent potential issues
        sanitized_filename = os.path.basename(file.filename)

        if file.content_length > MAX_SIZE:
            flash("Error: File too large", category="error")
            return render_template('error.html', message="Upload failed"), 500

        upload_file(file, sanitized_filename)  # Pass sanitized filename to function
    except Exception as e:
        exception_logger.error(repr(e))  # Use repr() for safer string construction

        flash("Error uploading file: " + str(e), category="error")

        return render_template('error.html', message="Upload failed"), 500

def upload_file(file, sanitized_filename):
    try:
        # Save the file to disk
        file.save(os.path.join(UPLOAD_FOLDER, sanitized_filename))

        flash("File uploaded successfully!", category="success")

        return redirect(url_for('review.show_review'))
    except OSError as e:
        exception_logger.error(repr(e))  # Use repr() for safer string construction

        flash("Error writing to disk: " + str(e), category="error")

app = Flask(__name__)

init_app(app)

@app.route('/test-upload', methods=['POST'])
@login_required
def test_upload():
    upload_file_view()
