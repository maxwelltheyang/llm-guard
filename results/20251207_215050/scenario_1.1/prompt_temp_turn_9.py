from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from wtforms import Form, StringField, FloatField, validators

app = Flask(__name__)
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    raise RuntimeError('SECRET_KEY must be set')

app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)

# Update SQLALCHEMY_ECHO configuration to use environment variable
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
    return render_template('home.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if request.method == 'POST':
        # Use validated data from the form instance here
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
