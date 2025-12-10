from flask import Flask, request, send_from_directory, jsonify
import os
import mimetypes

app = Flask(__name__)

# Define the directory where files will be stored using an environment variable
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/path/to/default/folder')

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # Validate the uploaded file type
    allowed_mime_types = {'image/jpeg', 'image/png', 'application/pdf'}
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type not in allowed_mime_types:
        return jsonify({'error': 'Invalid file type'}), 400

    # Validate the uploaded file size (1MB for example)
    max_size_mb = 1
    file_size = int(os.path.getsize(os.path.join(UPLOAD_FOLDER, file.filename)))
    if file_size <= 0 or file_size > max_size_mb * 1024 * 1024:
        return jsonify({'error': 'File is empty or too large'}), 400

    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return jsonify({'message': f'File {filename} uploaded successfully'}), 201

@app.route('/download/<string:filename>', methods=['GET'])
def download_file(filename):
    if not os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return jsonify({'error': 'File not found'}), 404

    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', False)
    app.run(debug=debug_mode)
