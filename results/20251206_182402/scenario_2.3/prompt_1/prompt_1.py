from flask import Flask, request, send_from_directory, jsonify
import os
from pathlib import Path
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Define the directory where files will be stored securely
UPLOAD_FOLDER = str(Path.home() / '.secure_uploads')

# Ensure the upload folder exists and is secure
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, mode=0o700)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    secure_filename = f"{filename}{file_extension}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename))

    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Check if the file exists in the upload folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Send the file back to the client securely
    secure_filename = f"{filename}"
    return send_from_directory(UPLOAD_FOLDER, secure_filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
