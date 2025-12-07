from flask import Flask, request, send_from_directory, jsonify
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

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

handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

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
    secure_filename = file.filename
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
        secure_filename = f"{filename}"
        return send_from_directory(UPLOAD_FOLDER, secure_filename, as_attachment=True)
    except PermissionError:
        logging.error(f"Permission denied when trying to send file {filename}")
        return jsonify({'error': 'Permission denied'}), 403
    except OSError as e:
        logging.error(f"OSError occurred when trying to send file {filename}: {e}")
        return jsonify({'error': 'Failed to send file'}), 500

if __name__ == '__main__':
    app.run()
