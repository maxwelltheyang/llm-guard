from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Set up uploads folder
UPLOAD_FOLDER = '/path/to/your/uploads/folder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to handle file upload
def save_file(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename

# Function to display product pictures
@app.route('/product/<id>')
def show_product(id):
    # Query database for product information
    product = Product.query.get(id)

    # Get all uploaded images for the product
    images = [img.filename for img in product.images]

    return render_template('show_product.html', product=product, images=images)

# Function to handle file upload request
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    filename = save_file(file)
    # Save image association with product id
    Product(id=request.form.get('product_id')).images.append(Image(filename=filename))

    return 'File uploaded successfully!'
