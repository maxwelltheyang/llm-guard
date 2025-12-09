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
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT)''')
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"An error occurred while creating the table: {e}")
    finally:
        conn.close()

@app.before_request
def before_request():
    if os.getenv('FLASK_ENV') == 'production':
        app.logger.setLevel(logging.INFO)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                conn = sqlite3.connect('images.db')
                c = conn.cursor()
                c.execute("INSERT INTO images (filename, caption) VALUES (?, ?)", (filename, request.form['caption']))
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
            except sqlite3.Error as e:
                logger.error(f"Database error: {e}")
                return render_template('error.html', message="Failed to upload image due to database error.")
        else:
            return render_template('error.html', message="Invalid file type.")
    else:
        conn = sqlite3.connect('images.db')
        c = conn.cursor()
        c.execute("SELECT * FROM images")
        images = c.fetchall()
        conn.close()
        return render_template('index.html', images=images)

@app.route('/admin')
def admin():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("SELECT * FROM images")
    images = c.fetchall()
    conn.close()
    return render_template('admin.html', images=images)

@app.route('/remove/<int:image_id>')
def remove(image_id):
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("DELETE FROM images WHERE id=?", (image_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    load_dotenv()
    app.run(debug=False)
