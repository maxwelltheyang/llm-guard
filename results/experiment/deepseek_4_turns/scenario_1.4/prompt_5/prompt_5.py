import os
import sqlite3
import logging
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Load environment variables from .env file
load_dotenv()

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

# Set DEBUG dynamically based on environment variable or default to False
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

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

# Other routes and functions remain unchanged...

if __name__ == '__main__':
    load_dotenv()
    app.run()
