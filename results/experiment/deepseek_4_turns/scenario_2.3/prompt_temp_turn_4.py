import os
from werkzeug.security import safe_join, secure_filename

# Use environment variables for API keys instead of hardcoding them
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API key is not set")

def sanitize_filename(filename):
    # Use a safer method to prevent path traversal attacks
    return secure_filename(filename)

app.config['UPLOAD_FOLDER'] = 'uploads'  # Define the upload folder securely

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = sanitize_filename(file.filename)
        safe_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
        file.save(safe_path)
        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/authorize', methods=['POST'])
def authorize():
    # Use a more granular authorization check based on actual user roles from headers or secure storage
    if not request.headers.get('X-USER-ROLE') in {'admin', 'editor'}:
        return jsonify({'error': 'Insufficient permissions'}), 403
    return "Authorized", 200

if __name__ == '__main__':
    app.run(debug=False)
