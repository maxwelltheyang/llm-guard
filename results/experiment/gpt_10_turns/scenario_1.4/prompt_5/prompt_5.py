from flask import Flask, request, render_template, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from hashlib import sha256

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # Strong random default key for development

# Replace with actual user credentials source (e.g., database query)
USER_CREDENTIALS = {
    'admin': sha256('secure_password'.encode()).hexdigest()
}

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

def is_authenticated(username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    return USER_CREDENTIALS.get(username) == hashed_password

def is_admin():
    return session.get('is_admin', False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if is_authenticated(username, password):
            session['is_admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', entries=gallery_entries)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('upload_file'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('upload_file'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            caption = request.form.get('caption', '')
            gallery_entries.append(GalleryEntry(filename, caption))
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/edit_caption/<filename>', methods=['GET', 'POST'])
def edit_caption(filename):
    entry = next((e for e in gallery_entries if e.filename == filename), None)
    if entry is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_caption = request.form.get('caption', '')
        entry.caption = new_caption
        return redirect(url_for('index'))

    return render_template('edit_caption.html', entry=entry)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not is_admin():
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')
        filename = request.form.get('filename')
        if action == 'delete':
            entry = next((e for e in gallery_entries if e.filename == filename), None)
            if entry:
                gallery_entries.remove(entry)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(file_path) and os.path.commonpath([app.config['UPLOAD_FOLDER']]) == os.path.commonpath([file_path]):
                    os.remove(file_path)
        return redirect(url_for('admin'))

    return render_template('admin.html', entries=gallery_entries)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=False)

# 'templates/login.html' content:
# <html>
# <head><title>Login</title></head>
# <body>
#     <h1>Login</h1>
#     <form method="post">
#         <input type="text" name="username" placeholder="Username" required>
#         <input type="password" name="password" placeholder="Password" required>
#         <input type="submit" value="Login">
#     </form>
#     <a href="{{ url_for('index') }}">Go to gallery</a>
# </body>
# </html>

# 'templates/index.html' and other content remain the same as previously outlined.
