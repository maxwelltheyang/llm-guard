import os
import logging
from flask import Flask, request, send_file, abort, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = os.urandom(24)  # For CSRF protection
app.config['DEBUG'] = False  # Set debug to False in production

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return True
    else:
        logger.warning("Invalid file type attempted to upload: %s", filename)
        return False

def allowed_file(filename):
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return True
    else:
        logger.warning("Invalid file type attempted to upload: %s", filename)
        return "Invalid file type"

# CSRF Protection example with Flask-WTF
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField("File", validators=[DataRequired()])
    submit = SubmitField("Upload")

# Placeholder for actual authentication logic
def is_authenticated():
    # Replace with real authentication logic
    return True  # Simplified example, should be replaced

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if not is_authenticated():
        return "Not authenticated", 401

    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return "File uploaded successfully", 200
        else:
            return "Invalid file type", 400
    else:
        return render_template('upload.html', form=form)

# HTTPS Configuration for Development
if not app.debug:
    from flask_sslify import SSLify
    sslify = SSLify(app)
