from flask import Flask, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_DIRECTORY = 'uploads'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

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
    return jsonify({"message": f"File '{filename}' has been uploaded successfully"}), 201

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

if __name__ == '__main__':
    # Set debug to False by default
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
