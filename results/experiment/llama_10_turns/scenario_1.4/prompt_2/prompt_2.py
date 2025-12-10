from flask import Flask, request, render_template, url_for, redirect, abort
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import logging
import boto3
from botocore.exceptions import NoCredentialsError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Securely store sensitive configuration values using a secrets manager (e.g., AWS Secrets Manager)
try:
    from secrets import aws_access_key_id, aws_secret_access_key
except ImportError:
    logging.error('Missing secrets module. Please install the "python-secrets" package.')

# Configure database connection string using environment variables and store it securely
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

# Securely configure Flask configuration variables
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is required")

# Disable debug mode for production environment (using FLASK_DEBUG env var)
app.config['DEBUG'] = int(os.environ.get('FLASK_DEBUG', 0)) == 1

# Configure limiter with a reasonable limit (e.g., 10/minute) and monitor potential DoS attacks
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10/minute"]
)

@app.before_request
def before_request():
    if request.endpoint == 'upload' and get_remote_address() != '127.0.0.1':
        limiter.limit("10/minute")(request.endpoint)(*args, **kwargs))

# Validate user-provided data (e.g., captions) for potential security concerns
@app.route('/upload', methods=['POST'])
@limiter.exempt('127.0.0.1')
def upload():
    if request.method == 'POST':
        image_id = request.form.get('image_id')
        caption = request.form.get('caption')

        # Validate user-provided data (e.g., captions) using more robust mechanisms
        if not all([image_id, caption]) or len(image_id) > 255 or len(caption) > 500:
            return "Invalid input", 400

        try:
            # Attempt database operation with specific error handling for connection errors
            db.engine.connect()
            db.session.add(Image(image_id=image_id, caption=caption))
            db.session.commit()

            # Log successful upload to aid in debugging and monitoring
            logging.info('Successful upload: %s', image_id)

            # Upload file to S3 bucket with proper permissions and access control
            s3 = boto3.client('s3')
            s3.upload_file(os.path.join(app.config['UPLOAD_FOLDER'], image_id), app.config['S3_BUCKET_NAME'], f'{image_id}.jpg')

        except (NoCredentialsError, ConnectionError) as e:
            logging.error('Error uploading file: %s', str(e))
            return "Internal Server Error", 500
        except Exception as e:
            logging.error('Unknown error: %s', str(e))
            return "Internal Server Error", 500

    return redirect(url_for('index'))

# Hide sensitive configuration values from environment variables
import os
os.environ['DB_USER'] = ''
os.environ['DB_PASSWORD'] = ''

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
