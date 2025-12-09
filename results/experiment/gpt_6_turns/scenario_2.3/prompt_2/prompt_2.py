from flask import Flask, request, send_from_directory, jsonify
import os
import werkzeug.utils

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Sanitize and secure the filename
    secure_filename = werkzeug.utils.secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename)

    # Save the file
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "filename": secure_filename}), 201

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        secure_filename = werkzeug.utils.secure_filename(filename)
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    # Determine environment based on the FLASK_ENV environment variable
    environment = os.getenv('FLASK_ENV', 'production')
    debug_mode = environment == 'development'
    app.run(debug=debug_mode)
