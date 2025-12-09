import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file name or type'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File uploaded successfully", 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/metadata', methods=['POST'])
def upload_metadata():
    metadata = request.files['metadata']
    if not metadata or metadata.filename == '':
        return jsonify({'error': 'No metadata file provided'}), 400
    if metadata and allowed_file(metadata.filename):
        # Validate the content type of the metadata file
        allowed_mimetypes = {'application/json'}
        if metadata.content_type not in allowed_mimetypes:
            return jsonify({'error': 'Invalid content type'}), 400
        filename = secure_filename(metadata.filename)
        metadata.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "Metadata uploaded successfully", 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/authorize', methods=['POST'])
def authorize():
    # Use a more granular authorization check based on actual user roles from headers or secure storage
    if not request.headers.get('X-USER-ROLE') in {'admin', 'editor'}:
        return jsonify({'error': 'Insufficient permissions'}), 403
    return "Authorized", 200

def sanitize_filename(filename):
    # Use a safer method to prevent path traversal attacks, such as using secure_filename from Werkzeug
    return secure_filename(filename)

if __name__ == '__main__':
    app.run(debug=False)
