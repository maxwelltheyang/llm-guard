from flask import Flask, request, send_from_directory, jsonify
import os
import mimetypes
import pathlib
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging.config
import sys

# Load environment variables securely and validate upload folder permissions
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
if UPLOAD_FOLDER is None:
    raise ValueError("UPLOAD_FOLDER environment variable is not set")
elif not os.path.exists(UPLOAD_FOLDER) or not os.access(UPLOAD_FOLDER, os.W_OK):
    raise ValueError("Invalid UPLOAD_FOLDER")

# Validate file types based on MIME type checking and whitelisting
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'application/json']

def validate_file_type(file_data):
    mime_type = mimetypes.guess_type(secure_filename(file_data.filename))[0]

    if mime_type in ALLOWED_MIME_TYPES:
        return mime_type
    else:
        logger.error(f"Invalid MIME type: {mime_type} for file: {file_data.filename}", exc_info=True)
        return None

# Send files with restrictive permissions (only read access for the owner)
def custom_send_file(filename, **kwargs):
    try:
        file_data = request.files['file']

        mime_type = validate_file_type(file_data)

        if mime_type in ALLOWED_MIME_TYPES:
            # Check if the file has a valid extension using pathlib
            if not (pathlib.Path(secure_filename(file_data.filename)).suffix in ['.jpg', '.png']):
                logger.error(f"Invalid file extension: {pathlib.Path(secure_filename(file_data.filename)).suffix} for file: {file_data.filename}", exc_info=True)
                return jsonify({'error': 'Invalid file extension'}), 400

            try:
                # Only send files with valid extensions
                if mime_type in ['image/jpeg', 'image/png']:
                    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename), as_attachment=True, attachment_filename=filename, **kwargs)
                else:
                    logger.error(f"Attempted RCE attack with filename: {filename}", exc_info=True)
                    return jsonify({'error': 'File not found'}), 404
            except Exception as e:
                logger.error(f"Error sending file: {e}", exc_info=True)
        else:
            logger.error(f"MIME type validation failed for file: {file_data.filename}", exc_info=True)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', False)

    app.send_file = custom_send_file

    # Create a custom error handler and add it to the application
    error_handler = CustomErrorHandler(app)

    if debug_mode:
        @app.errorhandler(404)
        def not_found(e):
            logger.error(f"404 Not Found: {e}", exc_info=True)
            return jsonify({'error': 'Not found'}), 404

        @app.errorhandler(500)
        def internal_server_error(e):
            logger.error(f"500 Internal Server Error: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

    # Run the application
    app.run()
