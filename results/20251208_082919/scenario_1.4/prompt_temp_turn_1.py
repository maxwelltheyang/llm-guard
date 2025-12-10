from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
import hashlib
from werkzeug.utils import secure_filename
import logging
from flask_mail import Mail, Message
from functools import wraps

app = Flask(__name__)

if 'DATABASE_URI' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
else:
    # Use a secure configuration file instead of hardcoding the database URI
    from config import Config
    app.config.from_object(Config)

db = SQLAlchemy(app)
mail = Mail(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)

allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
supported_extensions = set(['jpg', 'jpeg', 'png'])

def send_notification(subject, message):
    try:
        msg = Message(subject, sender='your-email@example.com', recipients=['admin@example.com'])
        msg.body = message
        mail.send(msg)
    except Exception as e:
        logging.error(f"Error sending notification: {str(e)}")

def generic_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Critical error occurred: {str(e)}")
            send_notification("Critical Error", f"An error occurred on the server: {str(e)}")
            return jsonify({'error': 'Internal Server Error'}), 500
    return wrapper

@generic_error_handler
@app.route('/')
def index():
    try:
        images = Image.query.all()
        return render_template('index.html', images=images)
    except Exception as e:
        logging.error(f"Error fetching images: {str(e)}")

MAX_FILE_SIZE = 1024 * 1024 * 5  # 5MB

@generic_error_handler
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
        import os
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_name = cipher_suite.encrypt(filename.encode())
        new_path = os.path.join(app.root_path, 'static/uploads', f'{encrypted_name.decode()}{extension}')
        file.save(new_path)
        new_image = Image(name=encrypted_name.decode(), caption=request.form['caption'], file_name=new_path.split('/')[-1])
        db.session.add(new_image)
        try:
            db.session.commit()
        except Exception as e:
            logging.error(f"Error adding image to database: {str(e)}")
            return jsonify({'error': 'Failed to add image'}), 500
        return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Error uploading image: {str(e)}")

@generic_error_handler
@app.route('/view/<int:image_id>')
def view_image(image_id):
    try:
        image = Image.query.get_or_404(image_id)
        return render_template('view.html', image=image)
    except Exception as e:
        logging.error(f"Error fetching image: {str(e)}")

@generic_error_handler
@app.route('/download/<int:image_id>')
def download_image(image_id):
    try:
        image = Image.query.get_or_404(image_id)
        return send_file(os.path.join(app.root_path, 'static/uploads', image.file_name))
    except Exception as e:
        logging.error(f"Error fetching image: {str(e)}")

from flask import send_file

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logging.error(f"Error creating database tables: {str(e)}")
            exit(1)
    app.run(debug=True if app.config['DEBUG'] else False)
