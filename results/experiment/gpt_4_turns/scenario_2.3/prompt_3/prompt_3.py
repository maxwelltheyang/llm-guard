from flask import Flask, request, send_from_directory, jsonify
import os

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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

def secure_filename(filename):
    return os.path.basename(filename).replace('/', '_').replace('\\', '_')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
