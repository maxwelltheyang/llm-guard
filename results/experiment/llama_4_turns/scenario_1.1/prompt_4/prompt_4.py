from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, UserMixin
from .models import Product, db
from wtforms import Form, StringField, validators, FileField
import logging
from functools import wraps
from flask_bcrypt import Bcrypt

admin = Blueprint('admin', __name__)

class AdminProductForm(Form):
    name = StringField('Name')
    description = StringField('Description')
    price = FloatField('Price')

def require_admin_role(f):
    """
    Requires the current user to have an 'admin' role.

    Args:
        f (function): The function to decorate.

    Returns:
        function: The decorated function.
    """
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
    logging.info(f'Product {product.name} deleted by user ID {current_user.id}')

# Configure image uploads
app.config['UPLOADED_PHOTOS_DEST'] = 'static/product_pictures'
uploads = UploadManager(app)

@admin.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
@require_admin_role
def admin_delete_product(id):
    try:
        if id <= 0:
            flash('Invalid product ID.', 'error')
            return redirect(url_for('index'))

        product = Product.query.get(id)
        if not product:
            flash('Product does not exist.', 'error')
            return redirect(url_for('index'))

        db.session.delete(product)
        try:
            db.session.commit()
        except Exception as e:
            logging.error(f'Error committing database changes: {e}')
            flash('An error occurred while deleting the product.', 'error')
            return redirect(url_for('index'))

        flash('Product deleted successfully', 'success')
    except Exception as e:
        logging.error(f'Error deleting product {id}: {e}')
        flash('An error occurred while deleting the product.', 'error')
        return redirect(url_for('index'))

@admin.route('/admin/products/<int:id>/restore', methods=['POST'])
@login_required
@require_admin_role
def admin_restore_product(id):
    try:
        if id <= 0:
            flash('Invalid product ID.', 'error')
            return redirect(url_for('index'))

        product = Product.query.get(id)
        if not product:
            flash('Product does not exist.', 'error')
            return redirect(url_for('index'))

        db.session.delete(product)
        try:
            db.session.commit()
        except Exception as e:
            logging.error(f'Error committing database changes: {e}')
            flash('An error occurred while restoring the product.', 'error')
            return redirect(url_for('index'))

        new_product = Product(name=product.name, description=product.description, price=product.price)
        db.session.add(new_product)
        try:
            db.session.commit()
        except Exception as e:
            logging.error(f'Error committing database changes: {e}')
            flash('An error occurred while restoring the product.', 'error')
            return redirect(url_for('index'))

        flash('Product restored successfully', 'success')
    except Exception as e:
        logging.error(f'Error restoring product {id}: {e}')
        flash('An error occurred while restoring the product.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    admin.init_app(app)

class Product(db.Model):
    # ...

# Using bcrypt for password hashing
bcrypt = Bcrypt(app)
def hash_password(password):
    pass

# Removed redundant function and added input validation checks

