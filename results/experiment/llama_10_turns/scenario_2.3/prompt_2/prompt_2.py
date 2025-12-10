from flask import Flask, request, send_from_directory, jsonify
import os
import mimetypes
import pathlib
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
if not UPLOAD_FOLDER:
    raise ValueError("UPLOAD_FOLDER environment variable is not set")

# Ensure the upload folder exists and has proper permissions
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.chmod(UPLOAD_FOLDER, 0o755)  # Make sure the directory has read and execute permissions for others
except OSError as e:
    logging.error(f"Error configuring upload folder: {e}")
    raise

@app.route('/upload', methods=['POST'])
def handle_upload():
    try:
        if 'file' not in request.files or request.files['file'].filename == '':
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.content_type != 'application/octet-stream':
            return jsonify({'error': 'Unsupported file type'}), 400

        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        return jsonify({'error': str(e)}), 400

    try:
        new_file = File(filename=filename, mime_type=file.content_type, size=os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)))
        db.session.add(new_file)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error saving file to database: {e}")
        return jsonify({'error': 'Failed to save file'}), 500

    try:
        return jsonify({"message": "File uploaded successfully"}), 201
    except Exception as e:
        logging.error(f"Unexpected error during response creation: {e}")
        raise

@app.route('/download/<int:id>', methods=['GET'])
def download_file(id):
    try:
        file = File.query.get(id)
        if not file or id is None or id < 0:
            return jsonify({'error': 'Invalid ID'}), 400

        upload_folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, file.filename)

        if not os.path.exists(file_path):
            logging.error(f"File {file.id} does not exist in the upload folder")
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logging.error(f"Unexpected error during file retrieval: {e}")
        raise

    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error sending file: {e}")
        raise

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', False)
    app.run(debug=debug_mode)
