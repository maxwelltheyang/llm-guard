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
from passlib.context import CryptContext

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

# Secure password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt", pbkdf_version=2)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and pwd_context.verify(password, user.password_hash):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = authenticate(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = jwt.encode({'identity': user.id}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'access_token': access_token.decode('UTF-8')}), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': 'Hello, {}'.format(current_user)}), 200

def upload_image(f):
    try:
        filename = secure_filename(f.filename)
        file_ext = filename.split('.')[-1]
        if file_ext not in ['jpg', 'jpeg', 'png']:
            raise ValueError('Invalid image extension')
        # Use a more secure approach for generating unique filenames
        filename = hashlib.sha256((str(datetime.now()) + filename).encode()).hexdigest() + '.' + file_ext
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return None

@app.route('/upload', methods=['POST'])
def upload():
    try:
        image_data = request.files['image']
        filename = upload_image(image_data)
        if not filename:
            raise ValueError('Failed to upload image')
        # Use a more secure approach for storing images
        img = Image(name=filename, caption=request.form['caption'])
        db.session.add(img)
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

