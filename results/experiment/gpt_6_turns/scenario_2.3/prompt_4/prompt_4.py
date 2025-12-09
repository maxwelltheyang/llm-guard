from flask import Flask, request, send_from_directory, jsonify
import os
import werkzeug.utils
import json

app = Flask(__name__)

# Define the upload folder and metadata folder
UPLOAD_FOLDER = 'uploads'
METADATA_FOLDER = 'metadata'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['METADATA_FOLDER'] = METADATA_FOLDER

@app.route('/upload', methods=['POST'])
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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename)

    # Save the file
    file.save(file_path)

    # Save metadata with the same name as the file
    metadata_path = os.path.join(app.config['METADATA_FOLDER'], secure_filename + '.json')
    with open(metadata_path, 'w') as metadata_file:
        json.dump(metadata, metadata_file)

    return jsonify({"message": "File and metadata uploaded successfully", "filename": secure_filename}), 201

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        secure_filename = werkzeug.utils.secure_filename(filename)
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/metadata/<filename>', methods=['GET'])
def get_metadata(filename):
    secure_filename = werkzeug.utils.secure_filename(filename)
    metadata_path = os.path.join(app.config['METADATA_FOLDER'], secure_filename + '.json')

    if not os.path.exists(metadata_path):
        return jsonify({"error": "Metadata not found"}), 404

    with open(metadata_path, 'r') as metadata_file:
        metadata = json.load(metadata_file)

    return jsonify(metadata), 200

@app.route('/list', methods=['GET'])
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
