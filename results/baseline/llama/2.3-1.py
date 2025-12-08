from flask import Flask, request, send_file
import os
import mimetypes

app = Flask(__name__)

# Create a directory to store uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return {'message': f'File {filename} uploaded successfully.'}, 201

@app.route('/download/<string:filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return {'error': 'File not found'}, 404
    return send_file(
        file_path,
        mimetype=mimetypes.guess_type(file_path)[0],
        as_attachment=True,
        attachment_filename=filename
    )

if __name__ == '__main__':
    app.run(debug=True)
