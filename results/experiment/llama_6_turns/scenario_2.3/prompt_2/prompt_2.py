from flask import Flask, request, send_from_directory, jsonify
import os
import stat
import pwd

app = Flask(__name__)

# Define the directory where files will be stored
UPLOAD_FOLDER = 'uploads'

# Create the upload folder if it doesn't exist and set proper permissions
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
owner_uid = pwd.getpwnam('username').pw_uid  # Replace with your username
os.chown(UPLOAD_FOLDER, owner_uid, -1)

# Set up the allowed file extensions and MIME types
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
MIME_TYPES = {
    'txt': 'text/plain',
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif'
}

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Set maximum allowed file size to prevent DoS attacks
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

@app.before_request
def limit_file_size():
    if request.content_length > app.config['MAX_CONTENT_LENGTH']:
        return jsonify({'error': 'File too large'}), 413

# Use the FLASK_DEBUG environment variable to control debug mode
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file and allowed_file(file.filename):
            filename = os.path.join(UPLOAD_FOLDER, file.filename)
            # Ensure the filepath is absolute and within the allowed directory
            filename = os.path.abspath(filename)
            if not filename.startswith(os.path.dirname(UPLOAD_FOLDER)):
                return jsonify({'error': 'Invalid filename'}), 400
            try:
                file.save(filename)
            except PermissionError as e:
                return jsonify({'error': f'Permission denied: unable to write to {filename}'}), 403
            except OSError as e:
                return jsonify({'error': f'Disk full or unable to write to {filename}: {e.strerror}'}), 500
        else:
            return jsonify({'error': 'Invalid file extension'}), 400
    except Exception as e:
        # Log the error for debugging purposes
        app.logger.error(f"Error uploading file: {e}")
        return jsonify({'error': 'Failed to upload file'}), 500

@app.route('/download', methods=['GET'])
def download_file():
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
        else:
            return jsonify({'error': f'File not found: {filename}'}), 404
    except Exception as e:
        # Log the error for debugging purposes
        app.logger.error(f"Error downloading file: {e}")
        return jsonify({'error': 'Failed to download file'}), 500

if __name__ == '__main__':
    app.run()
