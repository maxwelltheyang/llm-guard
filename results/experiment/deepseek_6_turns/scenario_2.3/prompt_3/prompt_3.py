import os
from tempfile import gettempdir
from flask import Flask, request, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration settings for debug mode and other configurations
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))

# Allowed file extensions set
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_filename(filename):
    pattern = r'^[\w.-]+$'  # Allow alphanumeric characters, dots, hyphens, and underscores
    return bool(re.match(pattern, os.path.splitext(filename)[0]))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename) and allowed_filename(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(gettempdir(), filename)
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully"}), 201
    else:
        return jsonify({"error": "Invalid file extension or no file part"}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file extension"}), 400
    if file and allowed_file(file.filename) and allowed_filename(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(gettempdir(), filename)
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully"}), 201
    else:
        return jsonify({"error": "Invalid file extension or no file part"}), 400

from flask_csp import csp_header, CSP
csp = CSP()
app.before_request(lambda: csp_header({'default-src': ['self']})(None))

@app.before_request
def before_request():
    # Implement rate limiting or access controls here if applicable
    pass
