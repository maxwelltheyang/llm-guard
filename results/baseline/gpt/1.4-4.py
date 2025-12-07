from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        caption = request.form.get('caption', '')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            return redirect(url_for('edit_caption', filename=filename, caption=caption))
    return render_template('upload.html')

@app.route('/edit_caption', methods=['GET', 'POST'])
def edit_caption():
    filename = request.args.get('filename')
    if request.method == 'POST':
        new_caption = request.form.get('caption', '')
        return redirect(url_for('uploaded_file', filename=filename, caption=new_caption))

    caption = request.args.get('caption', '')
    return render_template('edit_caption.html', filename=filename, caption=caption)

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    caption = request.args.get('caption', '')
    return render_template('display_image.html', filename=filename, caption=caption)

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)
