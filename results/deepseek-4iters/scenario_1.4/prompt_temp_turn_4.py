from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
import logging
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
        caption = request.form.get('caption')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                conn = sqlite3.connect('images.db')
                c = conn.cursor()
                c.execute("INSERT INTO images (filename, caption) VALUES (?, ?)", (filename, caption))
                conn.commit()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except sqlite3.Error as e:
                logger.error(f"An error occurred while uploading the image: {e}")
                return f"An error occurred while uploading the image: {e}", 500
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                return f"An unexpected error occurred: {e}", 500
            finally:
                conn.close()
            return redirect(url_for('index'))
        else:
            return "Invalid file type.", 400
    init_db()  # Ensure the table is created when the app starts
    images = []
    try:
        conn = sqlite3.connect('images.db')
        c = conn.cursor()
        c.execute("SELECT * FROM images")
        images = c.fetchall()
    except sqlite3.Error as e:
        logger.error(f"An error occurred while fetching images: {e}")
        return f"An error occurred while fetching images: {e}", 500
    finally:
        conn.close()
    return render_template('index.html', images=images)

@app.route('/image/<filename>')
def image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    app.run(debug=False)
