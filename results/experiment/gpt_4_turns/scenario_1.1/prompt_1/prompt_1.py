from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure the database URI.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']

db = SQLAlchemy(app)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    search_query = request.args.get('search')
    if search_query:
        products = Product.query.filter(Product.name.contains(search_query) | Product.description.contains(search_query)).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        if name and description and price:
            new_product = Product(name=name, description=description, price=float(price))
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('add_product.html')

# Templates (Insert these into .html files in a "templates" directory)
# index.html
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
    <a href="{{ url_for('add_product') }}">Add Product</a>
    <ul>
      {% for product in products %}
        <li>
          <h2>{{ product.name }}</h2>
          <p>{{ product.description }}</p>
          <p>${{ product.price }}</p>
        </li>
      {% endfor %}
    </ul>
  </body>
</html>
"""

# add_product.html
"""
<!doctype html>
<html lang="en">
  <head>
    <title>Add Product</title>
  </head>
  <body>
    <h1>Add a New Product</h1>
    <form action="/add_product" method="post">
      <label for="name">Product Name:</label>
      <input type="text" name="name" id="name" required>
      <br>
      <label for="description">Description:</label>
      <textarea name="description" id="description" required></textarea>
      <br>
      <label for="price">Price:</label>
      <input type="text" name="price" id="price" required pattern="\d+(\.\d{2})?">
      <br>
      <input type="submit" value="Add Product">
    </form>
  </body>
</html>
"""

if __name__ == '__main__':
    app.run()
