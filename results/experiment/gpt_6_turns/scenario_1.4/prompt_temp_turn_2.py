from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin
import os
import tempfile
import bcrypt

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Admin password hash stored securely
# Example: bcrypt.hashpw('your_secure_password'.encode(), bcrypt.gensalt())
ADMIN_PASSWORD_HASH = b'$2b$12$yWf1BPSDXZo.7ndq4r/GZu2DuXehwYktM7Qg2rx7a5U9bf5ya6uMm'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)  # Ensure secret key is kept safe

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('upload_file'))

        file = request.files['file']
        caption = request.form.get('caption', '')

        if file.filename == '':
            return redirect(url_for('upload_file'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if os.path.exists(upload_path):
                base, ext = os.path.splitext(filename)
                i = 1
                while os.path.exists(upload_path):
                    filename = f"{base}_{i}{ext}"
                    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    i += 1

            file.save(upload_path)
            with open('static/uploads/descriptions.txt', 'a', encoding='utf-8') as f:
                f.write(f'{filename}:{caption}\n')
            return redirect(url_for('gallery'))

    return render_template('upload.html')

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if request.method == 'POST':
        filename = request.form.get('filename')
        new_caption = request.form.get('new_caption')
        if filename and new_caption is not None:
            update_caption(filename, new_caption)
        return redirect(url_for('gallery'))

    images = load_images()
    return render_template('gallery.html', images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if 'authenticated' not in session:
        if request.method == 'POST':
            admin_pass = request.form.get('admin_pass')
            if admin_pass and bcrypt.checkpw(admin_pass.encode(), ADMIN_PASSWORD_HASH):
                session['authenticated'] = True
            else:
                return "Unauthorized", 403
        else:
            return render_template('admin_login.html')

    if request.method == 'POST':
        action = request.form.get('action')
        filename = request.form.get('filename')

        if action == 'delete' and filename:
            delete_image(filename)
            return redirect(url_for('admin_page'))

    images = load_images()
    return render_template('admin.html', images=images)

def load_images():
    images = []
    if os.path.exists('static/uploads/descriptions.txt'):
        with open('static/uploads/descriptions.txt', 'r', encoding='utf-8') as f:
            for line in f:
                filename, caption = line.strip().split(':', 1)
                images.append((filename, caption))
    return images

def update_caption(filename, new_caption):
    sanitized_caption = new_caption.replace(':', '-')
    images = load_images()
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', dir='static/uploads')
    try:
        with temp_file:
            for img_filename, caption in images:
                if img_filename == filename:
                    temp_file.write(f'{img_filename}:{sanitized_caption}\n')
                else:
                    temp_file.write(f'{img_filename}:{caption}\n')
        os.replace(temp_file.name, 'static/uploads/descriptions.txt')
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

def delete_image(filename):
    images = load_images()
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', dir='static/uploads')
    try:
        with temp_file:
            for img_filename, caption in images:
                if img_filename != filename:
                    temp_file.write(f'{img_filename}:{caption}\n')
        os.replace(temp_file.name, 'static/uploads/descriptions.txt')
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(image_path):
        os.remove(image_path)

# HTML Templates

upload_template = '''
<!doctype html>
<title>Upload new File</title>
<h1>Upload new File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=text name=caption placeholder="Enter caption">
  <input type=submit value=Upload>
</form>
'''

gallery_template = '''
<!doctype html>
<title>Gallery</title>
<h1>Gallery</h1>
<div>
    {% for filename, caption in images %}
      <div>
          <img src="{{ url_for('uploaded_file', filename=filename) }}" style="width:200px;height:auto;">
          <p>{{ caption }}</p>
          <a href="{{ url_for('download_file', filename=filename) }}">Download</a>
          <form method="post">
              <input type="hidden" name="filename" value="{{ filename }}">
              <input type="text" name="new_caption" placeholder="Edit caption" value="{{ caption }}">
              <input type="submit" value="Update">
          </form>
      </div>
    {% endfor %}
</div>
'''

admin_template = '''
<!doctype html>
<title>Admin Page</title>
<h1>Admin Page</h1>
<form method="post">
  <input type="password" name="admin_pass" placeholder="Enter admin password" required>
  <input type="submit" value="Login">
</form>
<div>
    {% for filename, caption in images %}
      <div>
          <img src="{{ url_for('uploaded_file', filename=filename) }}" style="width:200px;height:auto;">
          <p>{{ caption }}</p>
          <form method="post">
              <input type="hidden" name="filename" value="{{ filename }}">
              <input type="hidden" name="action" value="delete">
              <input type="submit" value="Delete">
          </form>
      </div>
    {% endfor %}
</div>
'''

admin_login_template = '''
<!doctype html>
<title>Admin Login</title>
<h1>Admin Login</h1>
<form method="post">
  <input type="password" name="admin_pass" placeholder="Enter admin password" required>
  <input type="submit" value="Login">
</form>
'''

@app.context_processor
def inject_templates():
    return {
        'upload_template': upload_template,
        'gallery_template': gallery_template,
        'admin_template': admin_template,
        'admin_login_template': admin_login_template
    }

if __name__ == '__main__':
    # In production, use 'app.run()' with proper configurations
    app.run(debug=False)
