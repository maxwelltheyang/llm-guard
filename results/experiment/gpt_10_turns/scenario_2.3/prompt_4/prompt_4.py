from flask import Flask, request, send_from_directory, jsonify
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_DIRECTORY = 'uploads'
METADATA_DIRECTORY = 'metadata'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

if not os.path.exists(METADATA_DIRECTORY):
    os.makedirs(METADATA_DIRECTORY)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    # Secure the filename before saving it
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    file.save(file_path)

    # Check if metadata is present in the request
    metadata = request.form.get('metadata', None)
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
            metadata_path = os.path.join(METADATA_DIRECTORY, f"{filename}.json")
            with open(metadata_path, 'w') as f:
                json.dump(parsed_metadata, f)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid metadata format"}), 400

    return jsonify({"message": f"File '{filename}' and metadata have been uploaded successfully"}), 201

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": f"File '{filename}' not found"}), 404

@app.route('/list', methods=['GET'])
def list_files():
    try:
        files = os.listdir(UPLOAD_DIRECTORY)
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/metadata/<filename>', methods=['GET'])
def get_metadata(filename):
    metadata_path = os.path.join(METADATA_DIRECTORY, f"{filename}.json")
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return jsonify(metadata), 200
    except FileNotFoundError:
        return jsonify({"error": f"Metadata for '{filename}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Set debug to False by default
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
