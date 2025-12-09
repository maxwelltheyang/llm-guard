from flask import Flask, request, send_from_directory, jsonify
import os
import json

app = Flask(__name__)

# Directories to save uploaded files and metadata
UPLOAD_FOLDER = 'uploads'
METADATA_FOLDER = 'metadata'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(METADATA_FOLDER):
    os.makedirs(METADATA_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['METADATA_FOLDER'] = METADATA_FOLDER
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Handle optional metadata
    metadata = request.form.get('metadata')
    if metadata:
        try:
            metadata_json = json.loads(metadata)
            with open(os.path.join(app.config['METADATA_FOLDER'], filename + '.json'), 'w') as f:
                json.dump(metadata_json, f)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON metadata"}), 400

    return jsonify({"message": f"File {filename} uploaded successfully"}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        filename = secure_filename(filename)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/list', methods=['GET'])
def list_files():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        files = [file for file in files if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], file))]
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving file list"}), 500

@app.route('/metadata/<filename>', methods=['GET'])
def get_metadata(filename):
    try:
        filename = secure_filename(filename) + '.json'
        with open(os.path.join(app.config['METADATA_FOLDER'], filename), 'r') as f:
            metadata = json.load(f)
        return jsonify(metadata), 200
    except FileNotFoundError:
        return jsonify({"error": "Metadata not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error reading metadata"}), 500

def secure_filename(filename):
    return os.path.basename(filename).replace('/', '_').replace('\\', '_')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
