from flask import Flask, request, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import tempfile
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import uuid

# Configure logging to log errors securely
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
DEBUG_MODE = os.environ.get('DEBUG_MODE') == 'True'

if DEBUG_MODE:
    SECRET_KEY = os.urandom(24)
else:
    # Load secret key from environment variable or secrets manager
    SECRET_KEY = os.environ['SECRET_KEY']

# Use consistent database approach between development and production environments
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_POOL_CLASS = 'flask_sqlalchemy.PooledSQLAlchemy'

# Set up Flask-SQLAlchemy with custom pool class
db = SQLAlchemy(app, pool_class=SQLALCHEMY_POOL_CLASS)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), unique=False, nullable=False)
    caption = db.Column(db.String(128), unique=False, nullable=True)

# Function to save caption for an image
def save_caption(image_id, caption):
    try:
        if not isinstance(caption, str) or len(caption.strip()) == 0:
            logger.error('Caption cannot be empty')
            raise ValueError('Caption cannot be empty')

        image = Image.query.get(image_id)
        if image:
            image.caption = caption
            db.session.commit()
            return True
        else:
            logger.error(f"Image with ID {image_id} not found")
            raise
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
    except ValueError as ve:
        logger.error(str(ve))
    except Exception as e:
        logger.error(f"Error saving caption: {str(e)}")
    finally:
        db.session.remove()

# Function to retrieve image by ID
def get_image(image_id):
    try:
        return Image.query.get(image_id)
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error retrieving image: {str(e)}")
    finally:
        db.session.remove()

if __name__ == '__main__':
    host = '127.0.0.1'  # Use a more restrictive binding in production
    port = 5000  # Use a fixed port for production

    if DEBUG_MODE:
        app.run(host=host, port=port)  
    else:
        # Use WSGI server like Gunicorn or uWSGI for production deployment
        import waitress
        waitress.serve(app, host=host, port=port)
