from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, UserMixin
from .models import Product, db
from wtforms import Form, StringField, validators
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

admin = Blueprint('admin', __name__)

class AdminProductForm(Form):
    name = StringField('Name')
    description = StringField('Description')
    price = FloatField('Price')

def require_admin_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            return redirect(url_for('index'))
        # Additional check to prevent users with admin role from modifying their own role
        if current_user.id == int(kwargs.get('id', 0)):
            flash('Cannot modify your own role', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def log_product_deletion(product):
    logging.info(f'Product {product.name} deleted by user {current_user.id}')

def create_product_instance(name, description, price, user_id):
    new_product = Product(name=name, description=description, price=price, user_id=user_id)
    return new_product

@admin.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
@require_admin_role
def admin_delete_product(id):
    try:
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()
        log_product_deletion(product)
        flash('Product deleted successfully', 'success')
    except Exception as e:
        logging.error(f'Error deleting product: {e}')
        flash('An error occurred while deleting the product.', 'error')
        db.session.rollback()
    return redirect(url_for('admin_products'))

@admin.route('/admin/products/<int:id>/restore', methods=['POST'])
@login_required
@require_admin_role
def admin_restore_product(id):
    try:
        product = Product.query.get(id)
        new_product = create_product_instance(product.name, product.description, product.price, current_user.id)
        db.session.delete(product)
        db.session.add(new_product)
        db.session.commit()
        flash('Product restored successfully', 'success')
    except Exception as e:
        logging.error(f'Error restoring product: {e}')
        flash('An error occurred while restoring the product.', 'error')
        db.session.rollback()
    return redirect(url_for('admin_products'))

if __name__ == '__main__':
    admin.init_app(app)

class ProductForm(Form):
    name = StringField('Name')
    description = StringField('Description')
    price = FloatField('Price')

# Using bcrypt for password hashing
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

class Product(db.Model):
    # ...
    @hybrid_property
    def version(self):
        return db.session.query(Product.version).filter(Product.id == self.id).scalar()

# Documentation for functions and classes
def require_admin_role(f):
    """
    Requires the current user to have an 'admin' role.

    Args:
        f (function): The function to decorate.

    Returns:
        function: The decorated function.
    """
