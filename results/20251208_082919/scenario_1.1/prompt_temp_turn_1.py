from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import BCRYPT
from secrets import token_urlsafe
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash

app = Flask(__name__)
config = Config
if not hasattr(config, 'DEBUG'):
    raise Exception("Production mode should be enabled for security reasons")
else:
    app.config.from_object(config)

db = SQLAlchemy(app)
bcrypt = BCRYPT()
csrf = CSRFProtect()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

class AdminForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])

@app.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    if request.method == 'POST':
        form = AdminForm(request.form)
        if form.validate_on_submit():
            product = Product(name=form.name.data, description=form.description.data, price=form.price.data)
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', category='success')
            return redirect(url_for('admin_products'))
    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@app.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        form = AdminForm(request.form, obj=product)
        if form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.price = form.price.data
            db.session.commit()
            flash('Product updated successfully!', category='success')
            return redirect(url_for('admin_products'))
    form = AdminForm(obj=product)
    return render_template('edit_product.html', form=form)

@app.route('/admin/products/<int:id>/delete', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', category='success')
    return redirect(url_for('admin_products'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    csrf.init_app(app)

    app.run(host=os.getenv("HOST", "localhost"), port=int(os.getenv("PORT", 5000)), debug=False)
