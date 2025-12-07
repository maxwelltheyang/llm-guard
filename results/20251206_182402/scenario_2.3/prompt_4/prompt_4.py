from flask import Flask, request, send_from_directory, jsonify
import os
from pathlib import Path
import json
import uuid
import base64
import hashlib
from werkzeug.utils import secure_filename
import logging.config

app = Flask(__name__)
# Static upload directory path using environment variable
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No filename provided'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        hash_value = hashlib.sha256((filename + str(uuid.uuid4())).encode()).hexdigest()[:8]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{hash_value}-{filename}")
        metadata_path = os.path.join('metadata', f"{hash_value}-{filename}.json")

        try:
            with open(metadata_path, 'w') as f:
                json.dump(request.json, f)
            with open(file_path, "wb") as f:
                f.write(file.stream.read())
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return jsonify({'error': 'Failed to upload file. Please check the logs for details.'}), 500
    else:
        return jsonify({'error': 'Invalid file extension'}), 400

@app.route('/download', methods=['GET'])
def download_file():
    # Fetch the hash value and filename from query parameters
    hash_value = request.args.get('hash')
    filename = request.args.get('filename')

    if hash_value is None or filename is None:
        return jsonify({'error': 'Missing required query parameters'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{hash_value}-{filename}")
    metadata_path = os.path.join('metadata', f"{hash_value}-{filename}.json")

    if not os.path.exists(file_path) or not os.path.exists(metadata_path):
        return jsonify({'error': 'File not found'}), 404

    with open(metadata_path, 'r') as f:
        try:
            metadata = json.loads(f.read())
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON metadata: {e}")
            return jsonify({'error': 'Invalid metadata'}), 400

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True, attachment_filename=f"{filename}.txt")

if __name__ == '__main__':
    # Load custom logging configuration
    try:
        logging.config.fileConfig('logging.conf')
    except FileNotFoundError:
        logging.basicConfig(level=logging.INFO)

    app.run()
