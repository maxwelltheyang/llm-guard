from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, StringField
import os
from werkzeug.utils import secure_filename
from functools import wraps
import tempfile
from pyfilesystem3 import Directory

app = Flask(__name__)
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # For development, generate a random secret key
    import secrets
    app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Use environment variables for sensitive data
app.config.from_envvar('APP_CONFIG_FILE')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def get_current_user():
    return g.current_user

@app.before_request
def load_current_user():
    g.current_user = current_user = get_current_user()
    if current_user:
        flask_login.login_user(current_user)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user and not request.blueprint in ['public']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        image_data = form.file.data.read()
        new_image = Image(name=filename, caption=form.name.data or 'Uploaded image')
        db.session.add(new_image)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        flash('Invalid file')
    return render_template('upload.html', form=form)

@app.route('/view/<int:image_id>')
@login_required
def view_image(image_id):
    if not g.current_user:
        flash('Access denied')
        return redirect(url_for('index'))

    image = Image.query.get_or_404(image_id)
    # Additional security measure: Verify user's access rights to the image
    if g.current_user.id == image.author_id or g.current_user.role == 'admin':
        return render_template('view.html', image=image)
    flash('Access denied')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True if os.environ.get('FLASK_ENV') == 'development' else False)
