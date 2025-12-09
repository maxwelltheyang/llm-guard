from flask import Flask, request, send_from_directory, jsonify
import os

app = Flask(__name__)

# Define the directory where files will be stored
UPLOAD_FOLDER = 'uploads'

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

# Set debug mode using the FLASK_DEBUG environment variable
app.config['DEBUG'] = bool(os.environ.get('FLASK_DEBUG', False))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
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
        except Exception as e:
            # Log the error for debugging purposes
            app.logger.error(f"Error saving file: {e}")
            return jsonify({'error': 'Failed to save file'}), 500
        return jsonify({'message': 'File uploaded successfully'}), 201
    else:
        return jsonify({'error': 'Invalid file extension'}), 400

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run()
