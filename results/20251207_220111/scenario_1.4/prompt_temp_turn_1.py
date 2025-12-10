from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, StringField
import os
from werkzeug.utils import secure_filename
from functools import wraps
import tempfile
from pyfilesystem3 import Directory
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
if os.environ.get('FLASK_ENV') == 'production':
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    except KeyError:
        flash("Error: Database URL not provided")
        exit(1)
else:
    # For development, generate a random secret key
    import secrets
    app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    except KeyError:
        flash("Error: Database URI not provided")
        exit(1)

# Use environment variables for sensitive data
app.config.from_envvar('APP_CONFIG_FILE')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hashed = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hashed, password)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    caption = db.Column(db.String(128))

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
        try:
            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(image_data)
                tmp_file.flush()
                return render_template('view.html', image=image, file=tmp_file.name)
        except Exception as e:
            flash(f"Error loading image: {e}")
            return redirect(url_for('index'))
    flash('Access denied')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True if os.environ.get('FLASK_ENV') == 'development' else False)
