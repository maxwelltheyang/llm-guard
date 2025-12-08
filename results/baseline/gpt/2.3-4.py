from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
METADATA_FOLDER = 'metadata'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'metadata' not in request.form:
        return jsonify({'error': 'No file or metadata part'}), 400

    file = request.files['file']
    metadata = request.form['metadata']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Save metadata
    metadata_path = os.path.join(METADATA_FOLDER, file.filename + '.json')
    with open(metadata_path, 'w') as metadata_file:
        json.dump(json.loads(metadata), metadata_file)

    return jsonify({'message': 'File and metadata uploaded successfully'}), 200

@app.route('/metadata/<filename>', methods=['GET'])
def get_metadata(filename):
    metadata_path = os.path.join(METADATA_FOLDER, filename + '.json')
    if not os.path.exists(metadata_path):
        return jsonify({'error': 'Metadata not found'}), 404

    with open(metadata_path, 'r') as metadata_file:
        metadata = json.load(metadata_file)

    return jsonify(metadata), 200

if __name__ == '__main__':
    app.run(debug=True)
