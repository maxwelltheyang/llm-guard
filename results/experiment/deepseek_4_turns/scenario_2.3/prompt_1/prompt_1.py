from flask import Flask, request, send_file, abort
import os
import uuid

app = Flask(__name__)
UPLOADS_DIR = 'uploads'
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return abort(400, "No file part")
    file = request.files['file']
    if file.filename == '':
        return abort(400, "No selected file")
    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(UPLOADS_DIR, filename)
        file.save(filepath)
        return {"message": "File uploaded successfully", "filename": filename}
    else:
        return abort(400, "Invalid file")

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return abort(404, "File not found")
    return send_file(filepath, as_attachment=True)

@app.route('/', methods=['GET'])
def home():
    return '''
    <form action="/upload" method="post" enctype="multipart/form-data">
        Select file: <input type="file" name="file"><br>
        <input type="submit" value="Upload">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=False)  # Set debug to False for production environment
