from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    products = Product.query.filter(Product.name.like(f'%{query}%')).all()
    return render_template('index.html', products=products, search=True, query=query)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
