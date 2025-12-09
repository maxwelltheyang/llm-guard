import os
from werkzeug.utils import secure_filename
import sqlite3
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def initialize_database():
    if not os.path.exists(DATABASE):
        with open('schema.sql') as f:
            get_db_connection().executescript(f.read())
        get_db_connection().commit()  # Ensure this line is correct and used with the right connection object

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_filename(filename):
    return secure_filename(filename)

@app.route('/')
def index():
    conn = get_db_connection()
    images = conn.execute('SELECT * FROM images').fetchall()
    conn.close()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))  # Use url_for to generate known URLs safely
    file = request.files['file']
    caption = request.form.get('caption', '')
    if file and allowed_file(file.filename):
        filename = os.path.join(UPLOAD_FOLDER, safe_filename(file.filename))
        if is_safe_path(request.host_url, filename):
            file.save(filename)
            conn = get_db_connection()
            conn.execute('INSERT INTO images (filename, caption) VALUES (?, ?)', (safe_filename(file.filename), caption))
            conn.commit()  # Ensure this line is correct and used with the right connection object
            conn.close()
    return redirect(url_for('index'))  # Use url_for to generate known URLs safely

if __name__ == '__main__':
    app.run(debug=False)  # Disable debug mode in production
