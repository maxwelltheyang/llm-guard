from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))

db.create_all()

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search']
        products = Product.query.filter(Product.name.contains(search_query)).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products)

@app.route("/add", methods=['POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    description = request.form['description']
    new_product = Product(name=name, price=price, description=description)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/product/<int:id>")
def product(id):
    product = Product.query.get_or_404(id)
    return render_template('product.html', product=product)

if __name__ == "__main__":
    app.run(debug=True)
