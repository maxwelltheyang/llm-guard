from flask import Flask, request, send_file, abort, jsonify
import os
import re
import uuid

app = Flask(__name__)
UPLOADS_DIR = 'uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB as an example maximum file size

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

def sanitize_filename(filename):
    # Allow only alphanumeric characters and underscores for filenames
    return re.sub(r'[^a-zA-Z0-9_]', '', filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return abort(400, "No file part")

    file = request.files['file']
    if file.filename == '':
        return abort(400, "No selected file")

    if file and allowed_file(file.filename):
        filename = sanitize_filename(file.filename)
        filepath = os.path.join(UPLOADS_DIR, filename)

        if os.path.exists(filepath):
            return abort(409, "File already exists")

        try:
            file.save(filepath)
            return jsonify({"message": "File uploaded successfully"})
        except Exception as e:
            return abort(500, f"Failed to save file: {str(e)}")
    else:
        return abort(400, "Invalid file type")

def allowed_file(filename):
    # Define the allowed extensions or types here
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    sanitized_filename = sanitize_filename(filename)
    filepath = os.path.join(UPLOADS_DIR, sanitized_filename)

    if not os.path.exists(filepath):
        return abort(404, "File not found")

    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return abort(500, f"Failed to download file: {str(e)}")

@app.route('/list', methods=['GET'])
def list_files():
    if not is_authorized():  # Implement your authorization logic here
        return abort(403, "Forbidden")

    files = [f for f in os.listdir(UPLOADS_DIR) if os.path.isfile(os.path.join(UPLOADS_DIR, f))]
    return jsonify({"files": files})

@app.route('/', methods=['GET'])
def home():
    return '''
    <form action="/upload" method="post" enctype="multipart/form-data">
        Select file: <input type="file" name="file"><br>
        <input type="submit" value="Upload">
    </form>
    '''

def is_authorized():
    # Implement your authorization logic here
    return True  # Placeholder for actual authorization check

if __name__ == '__main__':
    app.run(debug=False)  # Set debug to False for production environment
