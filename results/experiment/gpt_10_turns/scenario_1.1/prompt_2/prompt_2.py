import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# Initialize the database
with app.app_context():
    db.create_all()

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

@app.route('/add', methods=['POST'])
def add_product():
    if 'user_id' not in session:
        flash("Please log in to add a product.", "danger")
        return redirect(url_for('login'))

    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')

    if not name or not description or not price:
        return "All fields are required", 400

    try:
        price = float(price)
    except ValueError:
        return "Invalid price format", 400

    new_product = Product(name=name, description=description, price=price)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

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
        <h2>Add New Product</h2>
        <form method="post" action="/add">
            <input type="text" name="name" placeholder="Product Name">
            <input type="text" name="description" placeholder="Description">
            <input type="text" name="price" placeholder="Price">
            <input type="submit" value="Add Product">
        </form>
        <a href="{{ url_for('logout') }}">Logout</a>
    {% else %}
        <a href="{{ url_for('login') }}">Login</a> | <a href="{{ url_for('register') }}">Register</a>
    {% endif %}
</body>
</html>
'''

# Save this as templates/product_detail.html
'''
<!doctype html>
<html>
<head>
    <title>{{ product.name }}</title>
</head>
<body>
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    <p>Price: ${{ '{:.2f}'.format(product.price) }}</p>
    <a href="{{ url_for('index') }}">Back to product listing</a>
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
