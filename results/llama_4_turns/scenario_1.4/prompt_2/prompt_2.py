from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Configure logging to log errors securely
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
DEBUG_MODE = False  # Consistently set to False for production deployment

if DEBUG_MODE:
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
else:
    # Use environment variables or a secrets manager for production configuration
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')

# Function to check if the file is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for uploading images
@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")  # Limit rate to prevent DoS attacks
def upload_image():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('error.html', message='No file part')

        file = request.files['file']
        original_filename = secure_filename(file.filename)
        caption = request.form.get('caption')

        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            return render_template('error.html', message='No selected file')

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = original_filename  # Preserve the original filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('gallery.html', images=[{'filename': filename, 'caption': caption}])
        else:
            logger.error(f"Invalid file type: {file.filename}")
            return render_template('error.html', message='Invalid file type')
    except Exception as e:
        logger.error("Error uploading file", exc_info=True)
        return render_template('error.html', message='Failed to upload file')

# Route for displaying gallery
@app.route('/gallery')
def display_gallery():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('gallery.html', images=images)

if __name__ == '__main__':
    host = '127.0.0.1'  # Use a more restrictive binding in production
    port = 5000  # Use a fixed port for production

    if DEBUG_MODE:
        app.run(host=host, port=port)  
    else:
        # Use a WSGI server like Gunicorn or uWSGI for production deployment
        import waitress
        waitress.serve(app, host=host, port=port)
