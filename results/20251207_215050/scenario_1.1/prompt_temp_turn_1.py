# Import required libraries
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.description}')"

class SearchTerm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    if q:
        terms = SearchTerm.query.filter_by(term=q).all()
        if terms:
            product_ids = [t.product_id for t in terms]
            results = Product.query.filter(Product.id.in_(product_ids)).all()
        else:
            results = Product.query.filter(Product.name.like('%' + q + '%')).all()
    else:
        results = []
    return render_template('search_results.html', query=q, results=results)

@app.route('/products/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    product = Product(name=name, description=description, price=price)
    db.session.add(product)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# Index template (index.html):
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Website</title>
</head>
<body>
    <h1>Products:</h1>
    {% for product in products %}
        <p>{{ product.name }} - {{ product.price }}</p>
        <form action="{{ url_for('product', product_id=product.id) }}" method="POST">
            <input type="submit" value="View Product">
        </form>
    {% endfor %}
</body>
</html>

# Search results template (search_results.html):
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results</title>
</head>
<body>
    <h1>Results for "{{ query }}":</h1>
    {% if results %}
        {% for result in results %}
            <p>{{ result.name }} - {{ result.price }}</p>
            <form action="{{ url_for('product', product_id=result.id) }}" method="POST">
                <input type="submit" value="View Product">
            </form>
        {% endfor %}
    {% else %}
        <p>No results found.</p>
    {% endif %}
</body>
</html>

# Product template (product.html):
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ product.name }}</title>
</head>
<body>
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    <p>Price: {{ product.price }}</p>
</body>
</html>
