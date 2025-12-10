from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
import hashlib
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)

if 'DATABASE_URI' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
else:
    # Use a secure configuration file instead of hardcoding the database URI
    from config import Config
    app.config.from_object(Config)

db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)

allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
supported_extensions = set(['jpg', 'jpeg', 'png'])

@app.route('/')
def index():
    try:
        images = Image.query.all()
        return render_template('index.html', images=images)
    except Exception as e:
        logging.error(f"Error fetching images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images'}), 500

MAX_FILE_SIZE = 1024 * 1024 * 5  # 5MB

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if not request.files:
            return jsonify({'error': 'Invalid request'}), 400
        file = request.files['image']
        if file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large'}), 400
        filename, extension = os.path.splitext(file.filename)
        if extension[1:] not in supported_extensions:
            return jsonify({'error': 'Unsupported image type'}), 400
        sanitized_name = ''.join(c for c in secure_filename(filename) if c in allowed_chars)
        new_path = os.path.join(app.root_path, 'static/uploads', f'{sanitized_name}{extension}')
        file.save(new_path)
        new_image = Image(name=sanitized_name, caption=request.form['caption'], file_name=new_path.split('/')[-1])
        db.session.add(new_image)
        try:
            db.session.commit()
        except Exception as e:
            logging.error(f"Error adding image to database: {str(e)}")
            return jsonify({'error': 'Failed to add image'}), 500
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error uploading image: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

@app.route('/view/<int:image_id>')
def view_image(image_id):
    try:
        image = Image.query.get_or_404(image_id)
        return render_template('view.html', image=image)
    except Exception as e:
        logging.error(f"Error fetching image: {str(e)}")
        return jsonify({'error': 'Failed to fetch image'}), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logging.error(f"Error creating database tables: {str(e)}")
            exit(1)
    app.run(debug=True if app.config['DEBUG'] else False)
