import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)

# Configuration settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

# Allowed extensions for uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

def is_valid_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character"
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    reviews = db.relationship('Review', backref='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.name}>"

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __repr__(self):
        return f"<Review {self.content}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

with app.app_context():
    db.create_all()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        products = Product.query.filter(or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/admin')
@admin_required
def admin_panel():
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        file = request.files.get('file')

        if not name or not description or not price:
            flash("All fields are required.", "danger")
            return redirect(url_for('admin_add_product'))

        if not file or not allowed_file(file.filename):
            flash("An image file with a valid extension is required.", "danger")
            return redirect(url_for('admin_add_product'))

        try:
            price = float(price)
        except ValueError:
            flash("Invalid price format.", "danger")
            return redirect(url_for('admin_add_product'))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        new_product = Product(name=name, description=description, price=price, image_filename=filename)
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully.", "success")
        return redirect(url_for('admin_panel'))
    return render_template('admin_add_product.html')

@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price')
        file = request.files.get('file')

        if not product.name or not product.description or not product.price:
            flash("All fields are required.", "danger")
            return redirect(url_for('admin_edit_product', product_id=product_id))

        try:
            product.price = float(product.price)
        except ValueError:
            flash("Invalid price format.", "danger")
            return redirect(url_for('admin_edit_product', product_id=product_id))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            product.image_filename = filename

        db.session.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for('admin_panel'))
    return render_template('admin_edit_product.html', product=product)

@app.route('/admin/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for('admin_panel'))

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Please log in to submit a review.', 'danger')
            return redirect(url_for('login'))

        content = request.form.get('content')
        if not content:
            flash('Review content is required.', 'danger')
            return redirect(url_for('product_detail', product_id=product_id))

        new_review = Review(content=content, user_id=session['user_id'], product_id=product_id)
        db.session.add(new_review)
        db.session.commit()
        flash("Review added successfully.", "success")
        return redirect(url_for('product_detail', product_id=product_id))

    reviews = Review.query.filter_by(product_id=product_id).all()
    return render_template('product_detail.html', product=product, reviews=reviews)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first() is not None:
            flash('Username is already taken.', 'warning')
            return redirect(url_for('register'))

        validation_error = is_valid_password(password)
        if validation_error:
            flash(validation_error, 'warning')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
