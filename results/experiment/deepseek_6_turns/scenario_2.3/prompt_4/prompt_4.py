import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from tempfile import gettempdir
import json

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type or extension"}), 400

    try:
        metadata = request.json
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")

        filename = secure_filename(file.filename)
        filepath = os.path.join(gettempdir(), filename)  # Move this line up

        with open(filepath, 'wb') as f:
            file.save(f)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred while processing the file or metadata: {str(e)}"}), 500

    return jsonify({"message": "File and metadata uploaded successfully"}), 201
