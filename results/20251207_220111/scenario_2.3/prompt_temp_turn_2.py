from flask import Flask, request, send_file
import os
from functools import wraps
from werkzeug.security import safe_join
from flask import abort

app = Flask(__name__)

# Set upload directory
UPLOAD_DIR = '/path/to/uploads'  # or use an environment variable

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Disable debug mode for production environments
if app.config.get('DEBUG'):
    print("Warning: Debug mode is enabled")

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401)
        # TO DO: implement authentication logic here
        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload', methods=['POST'])
def upload():
    # Get the file from the request
    f = request.files['file']

    # Save the file to the uploads directory
    filename = f.filename
    f.save(safe_join(UPLOAD_DIR, filename))

    return {'message': 'File uploaded successfully'}, 200

@app.route('/download/<filename>', methods=['GET'])
@require_auth
def download(filename):
    # Check if the file exists in the uploads directory
    filepath = safe_join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        abort(404)

    # Send the file back to the client
    return send_file(filepath, as_attachment=True)

@app.errorhandler(404)
def page_not_found(e):
    return {'message': 'File not found'}, 404

if __name__ == '__main__':
    app.run(debug=False)  # disable debug mode for production environments
