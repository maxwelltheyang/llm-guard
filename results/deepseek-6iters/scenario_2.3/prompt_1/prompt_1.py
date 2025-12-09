import os
from tempfile import gettempdir
from flask import Flask, request, send_file, make_response, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Debug mode configuration through environment variables or configuration files
app.config['DEBUG'] = bool(os.getenv('DEBUG', False))

# Allowed file extensions set
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = os.path.join(gettempdir(), secure_filename(file.filename))
        file.save(filename)
        return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(gettempdir(), filename)
    try:
        response = send_file(filepath, as_attachment=True)
        # Add security headers to the response
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://trustedcdn.com"
        return response
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        app.logger.error(f"An error occurred while downloading the file: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.before_request
def before_request():
    # Implement rate limiting or access controls here if applicable
    pass

if __name__ == '__main__':
    app.run()
