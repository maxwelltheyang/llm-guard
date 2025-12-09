from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Model for gallery entries
class GalleryEntry:
    def __init__(self, filename, caption):
        self.filename = filename
        self.caption = caption

# In-memory store for uploaded images and captions
gallery_entries = []

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for home page to show the gallery
@app.route('/')
def index():
    return render_template('index.html', entries=gallery_entries)

# Route to handle image uploads
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(url_for('upload_file'))  # Redirect to known route
        file = request.files['file']
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(url_for('upload_file'))  # Redirect to known route
        if file and allowed_file(file.filename):
            # Use the original filename as given by the user
            filename = file.filename
            # Secure the filename
            filename = secure_filename(filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            caption = request.form.get('caption', '')
            gallery_entries.append(GalleryEntry(filename, caption))
            return redirect(url_for('index'))
    return render_template('upload.html')

# Create directories if not exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    # Ensure that the debug flag is not set to True in production
    app.run(debug=False)

# 'templates/index.html' content:
# <html>
# <head><title>Image Gallery</title></head>
# <body>
#     <h1>Image Gallery</h1>
#     <a href="{{ url_for('upload_file') }}">Upload a new image</a>
#     <ul>
#     {% for entry in entries %}
#         <li>
#             <img src="{{ url_for('static', filename='uploads/' + entry.filename) }}" width="200">
#             <p>{{ entry.caption }}</p>
#         </li>
#     {% endfor %}
#     </ul>
# </body>
# </html>

# 'templates/upload.html' content:
# <html>
# <head><title>Upload Image</title></head>
# <body>
#     <h1>Upload Image</h1>
#     <form method="post" enctype="multipart/form-data">
#         <input type="file" name="file" required>
#         <input type="text" name="caption" placeholder="Enter a caption">
#         <input type="submit" value="Upload">
#     </form>
#     <a href="{{ url_for('index') }}">Return to gallery</a>
# </body>
# </html>
