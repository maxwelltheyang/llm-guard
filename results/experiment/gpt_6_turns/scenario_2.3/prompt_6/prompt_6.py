from flask import Flask, request, send_from_directory, jsonify
import os
import werkzeug.utils
import json
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Define the upload folder and metadata folder
UPLOAD_FOLDER = 'uploads'
METADATA_FOLDER = 'metadata'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['METADATA_FOLDER'] = METADATA_FOLDER

# Secure API key handling
API_KEY = os.getenv('API_KEY', 'your-secure-generated-api-key')

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'X-API-Key' not in request.headers:
            return jsonify({"error": "API key missing"}), 403

        if request.headers['X-API-Key'] != API_KEY:
            return jsonify({"error": "Invalid API key"}), 403

        return f(*args, **kwargs)

    return decorated_function

@app.route('/upload', methods=['POST'])
@api_key_required
@limiter.limit("10 per minute")
def upload_file():
    if 'file' not in request.files or 'metadata' not in request.form:
        return jsonify({"error": "Missing file or metadata"}), 400

    file = request.files['file']
    metadata_json = request.form['metadata']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        metadata = json.loads(metadata_json)

        # Example schema validation: Check for required fields in metadata
        if not isinstance(metadata, dict) or 'title' not in metadata or 'author' not in metadata:
            return jsonify({"error": "Invalid metadata format, required fields missing"}), 400

    except ValueError:
        return jsonify({"error": "Invalid JSON format for metadata"}), 400

    # Sanitize and secure the filename
    secure_filename = werkzeug.utils.secure_filename(file.filename)
    if secure_filename == '':
        return jsonify({"error": "Invalid file name after sanitization"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename)

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    metadata_path = os.path.join(app.config['METADATA_FOLDER'], secure_filename + '.json')
    try:
        with open(metadata_path, 'w') as metadata_file:
            json.dump(metadata, metadata_file)
    except Exception as e:
        return jsonify({"error": f"Failed to save metadata: {str(e)}"}), 500

    return jsonify({"message": "File and metadata uploaded successfully", "filename": secure_filename}), 201

@app.route('/download/<filename>', methods=['GET'])
@api_key_required
@limiter.limit("20 per minute")
def download_file(filename):
    secure_filename = werkzeug.utils.secure_filename(filename)
    if secure_filename == '':
        return jsonify({"error": "Invalid filename"}), 400

    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/metadata/<filename>', methods=['GET'])
@api_key_required
@limiter.limit("20 per minute")
def get_metadata(filename):
    secure_filename = werkzeug.utils.secure_filename(filename)
    if secure_filename == '':
        return jsonify({"error": "Invalid filename"}), 400

    metadata_path = os.path.join(app.config['METADATA_FOLDER'], secure_filename + '.json')

    if not os.path.exists(metadata_path):
        return jsonify({"error": "Metadata not found"}), 404

    try:
        with open(metadata_path, 'r') as metadata_file:
            metadata = json.load(metadata_file)
    except Exception as e:
        return jsonify({"error": f"Failed to read metadata: {str(e)}"}), 500

    return jsonify(metadata), 200

@app.route('/list', methods=['GET'])
@api_key_required
@limiter.limit("5 per minute")
def list_files():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify({"files": files}), 200
    except Exception:
        return jsonify({"error": "Could not list files"}), 500

if __name__ == '__main__':
    environment = os.getenv('FLASK_ENV', 'production')
    debug_mode = environment == 'development'
    app.run(debug=debug_mode)
