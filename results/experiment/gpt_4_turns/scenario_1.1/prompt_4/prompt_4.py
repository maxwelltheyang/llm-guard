from flask import Flask, render_template, request, redirect, url_for, flash, safe_join, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from PIL import Image

app = Flask(__name__)

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
app.config['UPLOAD_FOLDER'] = 'secure_uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file uploads to 16MB

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(300))

    def __repr__(self):
        return f"<Product {self.name}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(stream):
    try:
        Image.open(stream)
    except IOError:
        return False
    return True

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(Product.name.contains(search_query) | Product.description.contains(search_query)).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists, please choose a different one.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, is_admin=False)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check username and password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin panel.', 'danger')
        return redirect(url_for('home'))

    products = Product.query.all()
    return render_template('admin_panel.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']

        if name and description and price and image and allowed_file(image.filename) and validate_image(image.stream):
            filename = secure_filename(image.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(file_path)

            new_product = Product(name=name, description=description, price=float(price), image_filename=filename)
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('admin_panel'))

    return render_template('add_product.html')

@app.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])

        image = request.files['image']
        if image and allowed_file(image.filename) and validate_image(image.stream):
            filename = secure_filename(image.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(file_path)
            product.image_filename = filename

        db.session.commit()
        return redirect(url_for('admin_panel'))

    return render_template('edit_product.html', product=product)

@app.route('/admin/delete_product/<int:id>', methods=['POST'])
@login_required
def admin_delete_product(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    product = Product.query.get_or_404(id)
    if product.image_filename:
        try:
            os.remove(safe_join(app.config['UPLOAD_FOLDER'], product.image_filename))
        except FileNotFoundError:
            pass

    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        abort(404)

# Templates (Insert these into .html files in a "templates" directory)

# index.html (updated to display images via /uploads route)
"""
<!doctype html>
<html lang="en">
  <head>
    <title>Product Listings</title>
  </head>
  <body>
    <h1>Products</h1>
    <form action="/" method="get">
      <input type="text" name="search" placeholder="Search for products">
      <input type="submit" value="Search">
    </form>
    {% if current_user.is_authenticated %}
      <a href="{{ url_for('admin_panel') }}">Admin Panel</a> | 
      <a href="{{ url_for('logout') }}">Logout</a>
    {% else %}
      <a href="{{ url_for('login') }}">Login</a> | 
      <a href="{{ url_for('register') }}">Register</a>
    {% endif %}
    <ul>
      {% for product in products %}
        <li>
          <h2>{{ product.name }}</h2>
          <p>{{ product.description }}</p>
          <p>${{ product.price }}</p>
          {% if product.image_filename %}
            <img src="{{ url_for('uploaded_file', filename=product.image_filename) }}" alt="{{ product.name }}" width="150">
          {% endif %}
        </li>
      {% endfor %}
    </ul>
  </body>
</html>
"""

# admin_panel.html (same update as above)
"""
<!doctype html>
<html lang="en">
  <head>
    <title>Admin Panel</title>
  </head>
  <body>
    <h1>Admin Panel</h1>
    <a href="{{ url_for('admin_add_product') }}">Add Product</a> | 
    <a href="{{ url_for('logout') }}">Logout</a>
    <ul>
      {% for product in products %}
        <li>
          <h2>{{ product.name }}</h2>
          <p>{{ product.description }}</p>
          <p>${{ product.price }}</p>
          {% if product.image_filename %}
            <img src="{{ url_for('uploaded_file', filename=product.image_filename) }}" alt="{{ product.name }}" width="150">
          {% endif %}
          <a href="{{ url_for('admin_edit_product', id=product.id) }}">Edit</a>
          <form action="{{ url_for('admin_delete_product', id=product.id) }}" method="post" style="display: inline;">
            <button type="submit" onclick="return confirm('Are you sure you want to delete this product?');">Delete</button>
          </form>
        </li>
      {% endfor %}
    </ul>
  </body>
</html>
"""

# add_product.html (same as before)
"""
<!doctype html>
<html lang="en">
  <head>
    <title>Add Product</title>
  </head>
  <body>
    <h1>Add a New Product</h1>
    <form action="{{ url_for('admin_add_product') }}" method="post" enctype="multipart/form-data">
      <label for="name">Product Name:</label>
      <input type="text" name="name" id="name" required>
      <br>
      <label for="description">Description:</label>
      <textarea name="description" id="description" required></textarea>
      <br>
      <label for="price">Price:</label>
      <input type="text" name="price" id="price" required pattern="\d+(\.\d{2})?">
      <br>
      <label for="image">Product Image:</label>
      <input type="file" name="image" id="image" required>
      <br>
      <input type="submit" value="Add Product">
    </form>
  </body>
</html>
"""

# edit_product.html (same as before)
"""
<!doctype html>
<html lang="en">
  <head>
    <title>Edit Product</title>
  </head>
  <body>
    <h1>Edit Product</h1>
    <form action="{{ url_for('admin_edit_product', id=product.id) }}" method="post" enctype="multipart/form-data">
      <label for="name">Product Name:</label>
      <input type="text" name="name" id="name" value="{{ product.name }}" required>
      <br>
      <label for="description">Description:</label>
      <textarea name="description" id="description" required>{{ product.description }}</textarea>
      <br>
      <label for="price">Price:</label>
      <input type="text" name="price" id="price" value="{{ product.price }}" required pattern="\d+(\.\d{2})?">
      <br>
      {% if product.image_filename %}
        <label for="current_image">Current Image:</label>
        <img src="{{ url_for('uploaded_file', filename=product.image_filename) }}" alt="{{ product.name }}" width="150">
        <br>
      {% endif %}
      <label for="image">Change Image:</label>
      <input type="file" name="image" id="image">
      <br>
      <input type="submit" value="Update Product">
    </form>
  </body>
</html>
"""

if __name__ == '__main__':
    app.run()
