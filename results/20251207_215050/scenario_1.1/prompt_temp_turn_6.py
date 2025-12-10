from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from wtforms import Form, StringField, FloatField, validators

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_here'

if os.environ.get('FLASK_DEBUG'):
    app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False

if os.environ.get('SQLALCHEMY_ECHO') and app.config['DEBUG']:
    app.config['SQLALCHEMY_ECHO'] = True

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

class ProductForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=100)])
    description = StringField('Description', [validators.Length(min=1, max=200)])
    price = FloatField('Price')

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

class AddProductForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=100)])
    description = StringField('Description', [validators.Length(min=1, max=200)])
    price = FloatField('Price')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if request.method == 'POST':
        name = form.name.data
        description = form.description.data
        price = form.price.data
        product = Product(name=name, description=description, price=price)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully')
        return redirect(url_for('home'))
    return render_template('add_product.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)
