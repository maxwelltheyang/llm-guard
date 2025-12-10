from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
import hashlib
from werkzeug.utils import secure_filename
import logging
from flask_mail import Mail, Message
from functools import wraps
import pytz
from datetime import datetime
import uuid

app = Flask(__name__)

if 'DATABASE_URI' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
else:
    # Use a secure configuration file instead of hardcoding the database URI
    from config import Config
    app.config.from_object(Config)

db = SQLAlchemy(app)
mail = Mail(app)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler('app.log')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)

@app.route('/upload', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        try:
            file = request.files['file']
            caption = request.form['caption']

            # Validate and normalize the filename before saving it to disk
            filename = secure_filename(file.filename)
            mime_type = file.mimetype
            extension = filename.split('.')[-1]
            if extension not in ['jpg', 'jpeg', 'png']:
                logger.error(f"Invalid image file uploaded")
                return jsonify({'error': 'Invalid image file'}), 400

            # Handle uploads securely (e.g., using cloud storage)
            uuid_filename = str(uuid.uuid4()) + '.' + extension
            file.save(os.path.join('static/uploads', uuid_filename))

            image = Image(name=uuid_filename, caption=caption, file_name=os.path.join('static/uploads', uuid_filename))
            db.session.add(image)
            try:
                db.session.commit()
            except Exception as e:
                logger.error(f"Error adding image to database: {str(e)}")
                return jsonify({'error': 'Failed to add image'}), 500
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            exit(1)
    # Use a secure IP address and port
    app.run(host='127.0.0.1', port=5000, debug=False)
