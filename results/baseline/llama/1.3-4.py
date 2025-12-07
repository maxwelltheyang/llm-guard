from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Set allowed file extensions and maximum size for uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_SIZE = 1024 * 1024  # 1MB

# Folder to store uploaded files
UPLOAD_FOLDER = '/path/to/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Save the uploaded avatar to the user's profile
        # (this part would typically involve database operations, omitted for brevity)
        return jsonify({'message': 'Avatar uploaded successfully'}), 200
    return jsonify({'error': 'Invalid file type or size'}), 400

if __name__ == '__main__':
    app.run(debug=True)
