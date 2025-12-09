from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
from urllib.parse import urlparse, urljoin

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

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
        if 'file' not in request.files or 'caption' not in request.form:
            return redirect(url_for('upload_file'))

        file = request.files['file']
        caption = request.form['caption']

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
    images = load_images()
    images_dict = {img[0]: img[1] for img in images}
    images_dict[filename] = caption
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'captions.txt'), 'w') as f:
        for fn, cp in images_dict.items():
            f.write(f'{fn},{cp}\n')

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

@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_caption(filename):
    if request.method == 'POST':
        new_caption = request.form.get('caption')
        if new_caption:
            save_caption(filename, new_caption)
        return redirect(url_for('gallery'))

    caption = next((caption for file, caption in load_images() if file == filename), '')
    return render_template('edit.html', filename=filename, caption=caption)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            images = load_images()
            return render_template('admin.html', images=images)
    return render_template('admin_login.html')

@app.route('/admin/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # Delete image file and update captions
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except FileNotFoundError:
        pass
    images = load_images()
    images = [img for img in images if img[0] != filename]
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'captions.txt'), 'w') as f:
        for fn, cp in images:
            f.write(f'{fn},{cp}\n')
    return redirect(url_for('admin_panel'))

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
      <a href="{{ url_for('download_file', filename=filename) }}">Download</a> | 
      <a href="{{ url_for('edit_caption', filename=filename) }}">Edit Caption</a>
    </div>
  {% endfor %}
</div>
<a href="{{ url_for('upload_file') }}">Upload Another Image</a>
"""

# edit.html
"""
<!doctype html>
<title>Edit Caption</title>
<h1>Edit Caption for {{ filename }}</h1>
<form method=post>
  <input type=text name=caption value="{{ caption }}">
  <input type=submit value="Update Caption">
</form>
<a href="{{ url_for('gallery') }}">Back to Gallery</a>
"""

# admin_login.html
"""
<!doctype html>
<title>Admin Login</title>
<h1>Admin Login</h1>
<form method=post>
  <input type=text name=username placeholder='Username'>
  <input type=password name=password placeholder='Password'>
  <input type=submit value="Login">
</form>
<a href="{{ url_for('gallery') }}">Back to Gallery</a>
"""

# admin.html
"""
<!doctype html>
<title>Admin Panel</title>
<h1>Admin Panel</h1>
<div>
  {% for filename, caption in images %}
    <div style="margin-bottom: 20px;">
      <img src="{{ url_for('uploaded_file', filename=filename) }}" style="max-width: 300px;"/><br>
      <strong>{{ caption }}</strong><br>
      <form method=post action="{{ url_for('delete_file', filename=filename) }}">
        <input type=submit value="Delete">
      </form>
    </div>
  {% endfor %}
</div>
<a href="{{ url_for('gallery') }}">Back to Gallery</a>
"""

if __name__ == '__main__':
    app.run()
