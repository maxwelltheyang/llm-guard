import os
import sqlite3
import logging
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure logging for better error handling and debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT)''')
    conn.commit()
    conn.close()

@app.before_request
def set_debug():
    if os.getenv('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        logger.setLevel(logging.INFO)

@app.errorhandler(sqlite3.Error)
def handle_db_error(e):
    logger.error(f"Database error: {e}")
    return render_template('error.html', message="An error occurred with the database."), 500

@app.route('/')
def index():
    try:
        conn = sqlite3.connect('images.db')
        c = conn.cursor()
        c.execute("SELECT * FROM images")
        images = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        return handle_db_error(e)

    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            conn = sqlite3.connect('images.db')
            c = conn.cursor()
            c.execute("INSERT INTO images (filename, caption) VALUES (?, ?)", (filename, request.form['caption']))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            return handle_db_error(e)
        return redirect(url_for('index'))
    else:
        return render_template('error.html', message="Invalid file type."), 400

@app.route('/admin')
def admin():
    try:
        conn = sqlite3.connect('images.db')
        c = conn.cursor()
        c.execute("SELECT * FROM images")
        images = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        return handle_db_error(e)

    return render_template('admin.html', images=images)

@app.route('/remove/<int:image_id>')
def remove(image_id):
    try:
        conn = sqlite3.connect('images.db')
        c = conn.cursor()
        c.execute("DELETE FROM images WHERE id=?", (image_id,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        return handle_db_error(e)

    return redirect(url_for('admin'))

if __name__ == '__main__':
    load_dotenv()
    app.run()
