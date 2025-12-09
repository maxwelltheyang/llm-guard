from flask import Flask, request, send_from_directory, jsonify
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from functools import wraps
import hashlib
import uuid
import base64

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Define the directory where files will be stored securely
UPLOAD_FOLDER = str(Path.home() / '.secure_uploads')

# Ensure the upload folder exists and is secure
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, mode=0o750)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import os
os.umask(0o077)

handler = logging.FileHandler('/var/log/app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        # Validate and hash the secret key
        secret_key_env = os.getenv('SECRET_KEY')
        if not secret_key_env:
            return jsonify({'error': 'Secret key not set'}), 500

        expected_secret_key_hash = hashlib.sha256(secret_key_env.encode()).hexdigest()
        actual_secret_key_hash = hashlib.sha256(auth_header.encode()).hexdigest()

        # Compare the hashed values
        if expected_secret_key_hash != actual_secret_key_hash:
            return jsonify({'error': 'Authentication failed'}), 401

        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # Check if the file has a valid extension
    allowed_extensions = ['txt', 'pdf', 'docx']
    filename, file_extension = os.path.splitext(file.filename)
    if file_extension[1:] not in allowed_extensions:
        return jsonify({'error': 'Only certain file types are allowed'}), 400

    # Save the file securely to disk
    secure_filename = secure_filename_generator(filename)
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename)):
        secure_filename = secure_filename_generator(filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename))

    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Check if the file exists in the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Send the file back to the client securely
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except PermissionError:
        logging.error(f"Permission denied when trying to send file {filename}")
        return jsonify({'error': 'Permission denied'}), 403
    except OSError as e:
        logging.error(f"OSError occurred when trying to send file {filename}: {e}")
        return jsonify({'error': 'Failed to send file'}), 500

@app.route('/download/<string:file_path>', methods=['GET'])
def download_file_path(file_path):
    try:
        # Check if the file exists in the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Send the file back to the client securely
        return send_from_directory(UPLOAD_FOLDER, file_path, as_attachment=True)
    except PermissionError:
        logging.error(f"Permission denied when trying to send file {file_path}")
        return jsonify({'error': 'Permission denied'}), 403
    except OSError as e:
        logging.error(f"OSError occurred when trying to send file {file_path}: {e}")
        return jsonify({'error': 'Failed to send file'}), 500

def secure_filename_generator(filename):
    filename = base64.b32encode(filename.encode()).decode()
    hash_value = hashlib.sha256((filename + str(uuid.uuid4())).encode()).hexdigest()[:8]
    return f"{hash_value}-{os.path.splitext(filename)[0]}"

if __name__ == '__main__':
    app.run()
