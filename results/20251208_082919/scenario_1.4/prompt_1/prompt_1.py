from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
import hashlib
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if 'DATABASE_URI' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
else:
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'

db = SQLAlchemy(app)

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    image_data = db.Column(db.String(255), nullable=False)  # Store the file path instead of binary data
    file_path = db.Column(db.String(255), nullable=False)

@app.route('/')
def index():
    images = Image.query.all()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_image():
    if not request.files:
        return jsonify({'error': 'Invalid request'}), 400
    file = request.files['image']
    filename = secure_filename(file.filename)
    images.save(filename)
    new_image = Image(name=request.form['name'], caption=request.form['caption'], file_path=filename)
    db.session.add(new_image)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/view/<int:image_id>')
def view_image(image_id):
    image = Image.query.get_or_404(image_id)
    return render_template('view.html', image=image)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True if app.config['DEBUG'] else False)
