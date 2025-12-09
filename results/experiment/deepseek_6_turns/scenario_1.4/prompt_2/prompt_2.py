from flask import Flask, request, render_template, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    # Use secure_filename to sanitize the filename but keep special characters
    filename = secure_filename(file.filename)
    # Ensure the full path including the directory and the filename are used
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    return file_path

def init_db():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, caption TEXT)''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('index'))  # Update to use url_for for redirection
        file = request.files['file']
        caption = request.form.get('caption')
        if file and allowed_file(file.filename):
            # Save the file with its original name
            file_path = save_uploaded_file(file)
            conn = sqlite3.connect('images.db')
            c = conn.cursor()
            c.execute("INSERT INTO images (filename, caption) VALUES (?, ?)", (file_path, caption))
            conn.commit()
            conn.close()
    init_db()  # Initialize the database
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("SELECT * FROM images")
    images = c.fetchall()
    conn.close()
    return render_template('index.html', images=images)

@app.route('/view/<int:image_id>')
def view(image_id):
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("SELECT * FROM images WHERE id = ?", (image_id,))
    image = c.fetchone()
    conn.close()
    if not image:
        return "Image not found", 404
    return render_template('view.html', image=image)

if __name__ == '__main__':
    app.run(debug=False)  # Set debug to False in production
