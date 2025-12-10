from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from config import Config

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.description}')"

class SearchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(100), nullable=False)
    result_ids = db.relationship('Product', secondary='search_result_product',
                                 backref=db.backref('search_results', lazy=True))

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    if q:
        # Use parameterized query to avoid SQL injection
        results = Product.query.filter(Product.name.like('%' + q + '%')).all()
        # Store the search result directly instead of individual terms
        search_result = SearchResult(query=q, result_ids=[result.id for result in results])
        db.session.add(search_result)
        db.session.commit()
    else:
        results = []
    return render_template('search_results.html', query=q, results=results)

@app.route('/products/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=app.config['HOST'], port=app.config['PORT'])
