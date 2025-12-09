from flask import Flask, request, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import tempfile
from flask_sqlalchemy import SQLAlchemy
import sqlite3

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
DEBUG_MODE = False  # Consistently set to False for production deployment

if DEBUG_MODE:
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
else:
    # Use environment variables or a secrets manager for production configuration
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Ensure consistent approach between dev and prod
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Image('{self.filename}')"

# Function to handle file upload
def upload_image(image_file):
    try:
        # Get the filename and extension from the uploaded image
        filename, ext = os.path.splitext(image_file.filename)

        # Create a secure filename by appending a unique ID
        filename += str(uuid.uuid4()) + ext

        # Save the uploaded image to the uploads folder with modified permissions
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as file:
            file.write(image_file.data)

        # Add the new image to the database
        new_image = Image(filename=filename)
        db.session.add(new_image)
        db.session.commit()

        return filename
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return None

# Function to handle file deletion
def delete_image(image_id):
    try:
        # Get the image from the database
        image = Image.query.get(image_id)

        if image:
            # Remove the image from the uploads folder
            path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            os.remove(path)

            # Delete the image from the database
            db.session.delete(image)
            db.session.commit()

            return True
        else:
            logger.error(f"Invalid image ID: {image_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return False

# Route for uploading images
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Check if the request contains a file
        if 'image' not in request.files:
            return "No image provided", 400

        # Get the uploaded image
        image_file = request.files['image']

        # Handle file upload
        filename = upload_image(image_file)

        if filename:
            return f"Image uploaded successfully: {filename}"
        else:
            return "Failed to upload image", 500
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return "Failed to upload image", 500

# Route for displaying gallery
@app.route('/')
def index():
    images = Image.query.all()
    return render_template('gallery.html', images=[{'filename': image.filename} for image in images])

# Route for deleting an image
@app.route('/delete/<int:image_id>')
def delete(image_id):
    try:
        # Handle file deletion
        if delete_image(image_id):
            return "Image deleted successfully"
        else:
            return "Failed to delete image", 500
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return "Failed to delete image", 500

if __name__ == '__main__':
    host = '127.0.0.1'  # Use a more restrictive binding in production
    port = 5000  # Use a fixed port for production

    if DEBUG_MODE:
        app.run(host=host, port=port)  
    else:
        # Use a WSGI server like Gunicorn or uWSGI for production deployment
        import waitress
        waitress.serve(app, host=host, port=port)
