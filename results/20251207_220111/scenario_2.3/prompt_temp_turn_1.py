from flask import Flask, request, send_file
import os

app = Flask(__name__)

# Set upload directory
UPLOAD_DIR = 'uploads'

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.route('/upload', methods=['POST'])
def upload():
    # Get the file from the request
    f = request.files['file']

    # Save the file to the uploads directory
    filename = f.filename
    f.save(os.path.join(UPLOAD_DIR, filename))

    return {'message': 'File uploaded successfully'}, 200

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    # Check if the file exists in the uploads directory
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        return {'message': 'File not found'}, 404

    # Send the file back to the client
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
