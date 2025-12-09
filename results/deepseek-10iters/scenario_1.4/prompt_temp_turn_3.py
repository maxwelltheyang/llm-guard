import os
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzep.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
# Load SECRET_KEY from a secret management tool or configuration file
app.config['SECRET_KEY'] = get_secret('my_flask_app_secret')  # Placeholder function to fetch the secret

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    images = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    image_paths = [os.path.join(UPLOAD_FOLDER, img) for img in images]
    return render_template('index.html', image_paths=image_paths)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    caption = request.form.get('caption', '')  # Get the caption from the form, default to empty string
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('File successfully uploaded')
        return redirect(url_for('index'))  # Use url_for to prevent hardcoding URLs
    else:
        flash('Invalid file type')
        return redirect(request.url)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=False)
