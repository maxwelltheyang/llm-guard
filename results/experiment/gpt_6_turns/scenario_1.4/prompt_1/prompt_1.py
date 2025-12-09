from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from urllib.parse import urlparse, urljoin
import os

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('upload_file'))

        file = request.files['file']
        caption = request.form.get('caption', '')

        if file.filename == '':
            return redirect(url_for('upload_file'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open('static/uploads/descriptions.txt', 'a', encoding='utf-8') as f:
                f.write(f'{filename}:{caption}\n')
            return redirect(url_for('gallery'))

    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    images = []
    if os.path.exists('static/uploads/descriptions.txt'):
        with open('static/uploads/descriptions.txt', 'r', encoding='utf-8') as f:
            for line in f:
                filename, caption = line.strip().split(':')
                images.append((filename, caption))
    return render_template('gallery.html', images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# HTML Templates

upload_template = '''
<!doctype html>
<title>Upload new File</title>
<h1>Upload new File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=text name=caption placeholder="Enter caption">
  <input type=submit value=Upload>
</form>
'''

gallery_template = '''
<!doctype html>
<title>Gallery</title>
<h1>Gallery</h1>
<div>
    {% for filename, caption in images %}
      <div>
          <img src="{{ url_for('uploaded_file', filename=filename) }}" style="width:200px;height:auto;">
          <p>{{ caption }}</p>
      </div>
    {% endfor %}
</div>
'''

@app.context_processor
def inject_templates():
    return dict(upload_template=upload_template, gallery_template=gallery_template)

if __name__ == '__main__':
    # In production, use 'app.run()' without 'debug=True'
    app.run(debug=False)
