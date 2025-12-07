from flask import Flask, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
METADATA_FOLDER = 'metadata'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'metadata' not in request.form:
        return jsonify({'error': 'No file or metadata provided'}), 400

    file = request.files['file']
    metadata = request.form['metadata']

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    metadata_path = os.path.join(METADATA_FOLDER, f"{file.filename}.json")

    file.save(file_path)
    with open(metadata_path, 'w') as f:
        f.write(metadata)

    return jsonify({'message': 'File and metadata uploaded successfully'})

@app.route('/metadata/<filename>', methods=['GET'])
def get_metadata(filename):
    metadata_path = os.path.join(METADATA_FOLDER, f"{filename}.json")

    if not os.path.exists(metadata_path):
        return jsonify({'error': 'Metadata not found'}), 404

    with open(metadata_path, 'r') as f:
        metadata = f.read()

    return jsonify(metadata)

if __name__ == '__main__':
    app.run(debug=True)
