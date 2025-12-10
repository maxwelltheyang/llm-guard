from flask import Flask, request, render_template, url_for
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    filename = db.Column(db.String(100))
    caption = db.Column(db.String(200))

# Create tables
with app.app_context():
    db.create_all()

# Set up logging with secure configuration
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('app.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_id(image_id):
    if not isinstance(image_id, str) or len(image_id) != 32:
        raise ValueError('Invalid image ID')

@app.errorhandler(404)
def page_not_found(e):
    return 'Image not found', 404

@app.errorhandler(ValueError)
def invalid_input(e):
    return str(e), 400

# Route for uploading image
@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['image']
        if file.filename == '':
            raise ValueError('No selected file')

        validate_image_id(request.form.get('id'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_image = Image(id=str(uuid4()), filename=filename, caption=request.form['caption'])
            db.session.add(new_image)

            try:
                # Catch specific exceptions related to database operations
                db.session.commit()
                logger.info('Image uploaded successfully')
                return 'Image uploaded successfully'
            except SQLAlchemyError as e:
                logger.error(f"Database error: {str(e)}")
                db.session.rollback()
                return "An unexpected error occurred", 500
            except Exception as e:
                # Catch any other exceptions that might occur during database operations
                logger.error(f"Unexpected error: {str(e)}")
                db.session.rollback()
                return "An unexpected error occurred", 500
        else:
            raise ValueError('File type not supported')
    except ValueError as e:
        return str(e), 400

# Route for displaying gallery
@app.route('/')
def index():
    try:
        images = Image.query.all()
        return render_template('gallery.html', images=images)
    except Exception as e:
        logger.error(f"Error retrieving images from database: {str(e)}")
        return "An error occurred", 500

# Route for viewing image details
@app.route('/view/<string:image_id>')
def view(image_id):
    try:
        validate_image_id(image_id)
        image = Image.query.filter_by(id=image_id).first()
        if image:
            return f'<img src="{{ url_for("static", filename="{image.filename}") }}" alt="Image {image.id}">' \
                   f'<p>Caption: {image.caption}</p>'
        else:
            raise ValueError('Invalid ID')
    except Exception as e:
        if isinstance(e, ValueError):
            return str(e), 404
        logger.error(f"An error occurred: {str(e)}")
        return "An error occurred", 500

# Route for serving static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))
