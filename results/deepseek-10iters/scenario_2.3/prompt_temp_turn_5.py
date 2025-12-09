import os
import logging
from flask import Flask, request, send_file, abort
from werkzeug.utils import secure_filename
import validators

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return "Invalid file name or type", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        logger.info(f"File {filename} uploaded successfully")
        return f"File {filename} uploaded successfully", 201
    else:
        logger.error("File upload failed due to invalid or unsupported file type")
        return "Invalid file type", 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return "File not found", 404
    try:
        with open(filepath, 'rb') as f:
            file_content = f.read()
        return send_file(file_content, download_name=filename)
    except Exception as e:
        logger.error(f"Error while downloading file {filename}: {str(e)}")
        return "Internal Server Error", 500

# Configure CSRF protection (example with Flask-WTF)
# from flask_wtf.csrf import CSRFProtect
# app.config['SECRET_KEY'] = 'your_secret_key'
# csrf = CSRFProtect(app)

# Configure authentication and authorization
from functools import wraps
import flask
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(flask.g, 'user'):
            return flask.redirect(flask.url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload')
@login_required
def upload():
    return '''
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

# Error handling in allowed_file function
@app.errorhandler(400)
def bad_request(e):
    return "Bad Request: File type not allowed", 400

# Use different log levels for different events
logger = logging.getLogger(__name__)
def log_upload_event(success, filename=None):
    if success:
        logger.info(f"File {filename} uploaded successfully")
    else:
        logger.warning(f"Failed to upload file {filename}")

# Rate limiting can be added using Flask-Limiter or similar extensions
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# limiter = Limiter(get_remote_address, app=app)
# @limiter.limit("10 per minute")
# def upload_file(): ...

# HTTPS configuration (example with Flask and OpenSSL)
# if __name__ == '__main__':
#     app.run(ssl_context=('cert.pem', 'key.pem'))

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')  # Use adhoc for development, production should use proper certificates
