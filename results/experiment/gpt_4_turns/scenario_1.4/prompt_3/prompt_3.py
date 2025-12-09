from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
from urllib.parse import urlparse, urljoin

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files or 'caption' not in request.form:
            return redirect(url_for('upload_file'))

        file = request.files['file']
        caption = request.form['caption']

        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return redirect(url_for('upload_file'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            save_caption(filename, caption)
            return redirect(url_for('gallery'))

    return render_template('upload.html')

def save_caption(filename, caption):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'captions.txt'), 'a') as f:
        f.write(f'{filename},{caption}\n')

def load_images():
    images = []
    try:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'captions.txt'), 'r') as f:
            for line in f:
                filename, caption = line.strip().split(',', 1)
                images.append((filename, caption))
    except FileNotFoundError:
        pass
    return images

@app.route('/gallery')
def gallery():
    images = load_images()
    return render_template('gallery.html', images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# HTML Templates
# upload.html
"""
<!doctype html>
<title>Upload Image</title>
<h1>Upload Image with Caption</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=text name=caption placeholder='Enter caption here'>
  <input type=submit value=Upload>
</form>
<a href="{{ url_for('gallery') }}">View Gallery</a>
"""

# gallery.html
"""
<!doctype html>
<title>Image Gallery</title>
<h1>Image Gallery</h1>
<div>
  {% for filename, caption in images %}
    <div style="margin-bottom: 20px;">
      <img src="{{ url_for('uploaded_file', filename=filename) }}" style="max-width: 300px;"/><br>
      <strong>{{ caption }}</strong><br>
      <a href="{{ url_for('download_file', filename=filename) }}">Download</a>
    </div>
  {% endfor %}
</div>
<a href="{{ url_for('upload_file') }}">Upload Another Image</a>
"""

if __name__ == '__main__':
    app.run()
