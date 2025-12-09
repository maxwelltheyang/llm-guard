import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for products
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        # Search for the products matching the query in both name and description
        products = Product.query.filter(or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )).all()
    else:
        # Show all products if no query is provided
        products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')

    # Input validation
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
    <h2>Add New Product</h2>
    <form method="post" action="/add">
        <input type="text" name="name" placeholder="Product Name">
        <input type="text" name="description" placeholder="Description">
        <input type="text" name="price" placeholder="Price">
        <input type="submit" value="Add Product">
    </form>
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

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
