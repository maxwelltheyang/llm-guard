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
import jwt

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
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Secret key management using environment variables
secret_key = os.environ.get('SECRET_KEY')

# JWT configuration
jwt_config = {
    'secret_key': secret_key,
    'algorithm': 'HS256',
}

def upload_image(f):
    try:
        filename = secure_filename(f.filename)
        file_ext = filename.split('.')[-1]
        if file_ext not in ['jpg', 'jpeg', 'png']:
            raise ValueError('Invalid image extension')
        # Use UUIDs for unique filenames
        filename = str(uuid.uuid4()) + '.' + file_ext
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

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        # Use JWT with secure secret key
        access_token = jwt.encode({'identity': username}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'access_token': access_token.decode('UTF-8')}), 200
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({'error': 'Failed to log in'}), 401

# Authentication and authorization using JWT
def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        try:
            identity = jwt.decode(access_token, secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Access token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid access token'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/protected', methods=['GET'])
@requires_auth()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': 'Hello, {}'.format(current_user)}), 200

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            exit(1)
    # Use a secure IP address and port
    app.run(host='127.0.0.1', port=5000, debug=False)

