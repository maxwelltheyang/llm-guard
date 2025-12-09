from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

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
def upload_image():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return render_template('error.html', message='No file part')

    file = request.files['file']
    caption = request.form.get('caption')

    # If user does not select file, browser also
    # submits an empty part without filename
    if file.filename == '':
        return render_template('error.html', message='No selected file')

    # Check if the file is allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('gallery.html', images=[{'filename': filename, 'caption': caption}])
    else:
        return render_template('error.html', message='Invalid file type')

# Route for displaying gallery
@app.route('/gallery')
def display_gallery():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('gallery.html', images=images)

if __name__ == '__main__':
    host = '127.0.0.1'  # Use a more restrictive binding in production
    port = 5000  # Use a fixed port for production

    if DEBUG_MODE:
        app.run(host=host, port=port)  # Consistently use the safer alternative even in development environments
    else:
        # Use a WSGI server like Gunicorn or uWSGI for production deployment
        import waitress
        waitress.serve(app, host=host, port=port)
