from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files or 'caption' not in request.form:
            return redirect(request.url)
        file = request.files['file']
        caption = request.form['caption']
        if file.filename == '' or caption == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open('data.txt', 'a') as f:
                f.write(f"{filename}|{caption}\n")
            return redirect(url_for('gallery'))
    return '''
    <!doctype html>
    <title>Upload new Image</title>
    <h1>Upload new Image</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=text name=caption placeholder="Enter Caption">
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/gallery')
def gallery():
    images = []
    if os.path.exists('data.txt'):
        with open('data.txt', 'r') as f:
            for line in f:
                filename, caption = line.strip().split('|')
                images.append({'filename': filename, 'caption': caption})
    return render_template('gallery.html', images=images)

# Create templates folder and add gallery.html file
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['_'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
    app.run(debug=True)
