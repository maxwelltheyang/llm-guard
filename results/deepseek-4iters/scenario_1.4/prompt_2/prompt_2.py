from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            return redirect(url_for('index'))  # Use url_for to generate secure URLs within the application
        file = request.files['file']
        caption = request.form.get('caption')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn = sqlite3.connect('images.db')
            c = conn.cursor()
            c.execute("INSERT INTO images (filename, caption) VALUES (?, ?)", (filename, caption))
            conn.commit()
            conn.close()
    init_db()
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("SELECT * FROM images")
    images = c.fetchall()
    conn.close()
    return render_template('index.html', images=images)

@app.route('/view/<int:id>')
def view(id):
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("SELECT * FROM images WHERE id=?", (id,))
    image = c.fetchone()
    conn.close()
    if not image:
        return "Image not found", 404
    return render_template('view.html', image=image)

if __name__ == '__main__':
    app.run(debug=False)  # Disable debug mode for production environment
