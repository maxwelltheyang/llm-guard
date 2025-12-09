import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

# Configuration settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

# Define a function to validate password strength
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

# Database models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# Initialize the database
with app.app_context():
    db.create_all()

def admin_required(f):
    """Decorator to restrict access to admin users only."""
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

        if not name or not description or not price:
            flash("All fields are required.", "danger")
            return redirect(url_for('admin_add_product'))

        try:
            price = float(price)
        except ValueError:
            flash("Invalid price format.", "danger")
            return redirect(url_for('admin_add_product'))

        new_product = Product(name=name, description=description, price=price)
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

        if not product.name or not product.description or not product.price:
            flash("All fields are required.", "danger")
            return redirect(url_for('admin_edit_product', product_id=product_id))

        try:
            product.price = float(product.price)
        except ValueError:
            flash("Invalid price format.", "danger")
            return redirect(url_for('admin_edit_product', product_id=product_id))

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

        # Validate the password
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

# HTML templates
# Save this as templates/index.html
'''
<!doctype html>
<html>
<head>
    <title>E-commerce Site</title>
</head>
<body>
    <h1>Product Listings</h1>
    <form method="get" action="/">
        <input type="text" name="query" placeholder="Search products">
        <input type="submit" value="Search">
    </form>
    <ul>
        {% for product in products %}
        <li>
            <a href="{{ url_for('product_detail', product_id=product.id) }}">{{ product.name }}</a>
            - ${{ '{:.2f}'.format(product.price) }}
        </li>
        {% endfor %}
    </ul>
    {% if 'user_id' in session %}
        <a href="{{ url_for('logout') }}">Logout</a>
        {% if User.query.get(session['user_id']).is_admin %}
            | <a href="{{ url_for('admin_panel') }}">Admin Panel</a>
        {% endif %}
    {% else %}
        <a href="{{ url_for('login') }}">Login</a> | <a href="{{ url_for('register') }}">Register</a>
    {% endif %}
</body>
</html>
'''

# Save this as templates/admin.html
'''
<!doctype html>
<html>
<head>
    <title>Admin Panel</title>
</head>
<body>
    <h1>Admin Panel</h1>
    <a href="{{ url_for('admin_add_product') }}">Add New Product</a>
    <ul>
        {% for product in products %}
        <li>
            {{ product.name }} - ${{ '{:.2f}'.format(product.price) }}
            <a href="{{ url_for('admin_edit_product', product_id=product.id) }}">Edit</a>
            <form action="{{ url_for('admin_delete_product', product_id=product.id) }}" method="post" style="display:inline-block;">
                <input type="submit" value="Delete">
            </form>
        </li>
        {% endfor %}
    </ul>
    <a href="{{ url_for('index') }}">Back to product listing</a>
</body>
</html>
'''

# Save this as templates/admin_add_product.html
'''
<!doctype html>
<html>
<head>
    <title>Add Product</title>
</head>
<body>
    <h1>Add New Product</h1>
    <form method="post" action="{{ url_for('admin_add_product') }}">
        <input type="text" name="name" placeholder="Product Name" required>
        <input type="text" name="description" placeholder="Description" required>
        <input type="text" name="price" placeholder="Price" required>
        <input type="submit" value="Add Product">
    </form>
    <a href="{{ url_for('admin_panel') }}">Back to Admin Panel</a>
</body>
</html>
'''

# Save this as templates/admin_edit_product.html
'''
<!doctype html>
<html>
<head>
    <title>Edit Product</title>
</head>
<body>
    <h1>Edit Product</h1>
    <form method="post" action="{{ url_for('admin_edit_product', product_id=product.id) }}">
        <input type="text" name="name" placeholder="Product Name" value="{{ product.name }}" required>
        <input type="text" name="description" placeholder="Description" value="{{ product.description }}" required>
        <input type="text" name="price" placeholder="Price" value="{{ product.price }}" required>
        <input type="submit" value="Update Product">
    </form>
    <a href="{{ url_for('admin_panel') }}">Back to Admin Panel</a>
</body>
</html>
'''

# Save this as templates/register.html
'''
<!doctype html>
<html>
<head>
    <title>Register</title>
</head>
<body>
    <h1>Register</h1>
    <form method="post" action="{{ url_for('register') }}">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <input type="submit" value="Register">
        <p>Password must be at least 8 characters, contain an uppercase letter, a lowercase letter, a number, and a special character.</p>
    </form>
    <a href="{{ url_for('login') }}">Already have an account? Login here</a>
</body>
</html>
'''

# Save this as templates/login.html
'''
<!doctype html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <form method="post" action="{{ url_for('login') }}">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <input type="submit" value="Login">
    </form>
    <a href="{{ url_for('register') }}">Don't have an account? Register here</a>
</body>
</html>
'''

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
