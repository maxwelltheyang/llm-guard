from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from yourapp.models import Product, db
import re
import decimal
from functools import wraps
from datetime import datetime, timedelta
from config import MAX_CALLS, TIMEOUT

admin_panel = Blueprint('admin_panel', __name__, template_folder='templates')

# Create a database table to store rate limit data if it doesn't exist yet
class RateLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100), unique=True)
    max_calls = db.Column(db.Integer)
    timeout = db.Column(db.Interval)

def get_rate_limit(ip_address):
    rate_limit = RateLimit.query.filter_by(ip_address=ip_address).first()
    if rate_limit:
        return rate_limit.max_calls, rate_limit.timeout
    else:
        return MAX_CALLS, TIMEOUT  # Default max calls and timeout

@admin_panel.route('/admin/products', methods=['GET'])
@login_required
@requires_admin_access
def products():
    if not current_user.is_admin:
        flash("Access denied.", category="error")
        return redirect(url_for('login'))

    products = Product.query.all()
    return render_template('products.html', products=products)

@admin_panel.route('/admin/products/add', methods=['POST'])
@login_required
@requires_admin_access
def add_product():
    if not current_user.is_admin:
        flash("Access denied.", category="error")
        return redirect(url_for('login'))

    name = request.form['name']
    price = decimal.Decimal(request.form['price'])

    # Validate user input using regular expression and decimal validation
    if not re.match(r'^[a-zA-Z0-9\s]+$', name):
        flash("Invalid product name. Please try again.", category="error")
        return redirect(url_for('admin_panel.products'))
    elif price < 0:
        flash("Price cannot be negative.", category="error")
        return redirect(url_for('admin_panel.products'))

    new_product = Product(name=name, price=price)
    db.session.add(new_product)
    db.session.commit()

    flash("Product added successfully!", category="success")
    return redirect(url_for('admin_panel.products'))

@admin_panel.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
@requires_admin_access
def delete_product(id):
    if not current_user.is_admin:
        flash("Access denied.", category="error")
        return redirect(url_for('login'))

    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()

        # Check if the user has previously deleted products
        if Product.query.filter_by(deleted=True).count() > 0:
            flash("You have already deleted products!", category="warning")
        else:
            flash("Product deleted successfully!", category="success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting product: " + str(e), category="error")

    return redirect(url_for('admin_panel.products'))

def requires_admin_access(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access denied.", category="error")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

@admin_panel.before_request
def csrf_protect():
    token = request.form.get('csrf_token')
    if token != current_user.csrf_token:
        flash("Invalid CSRF token", category="error")
        return redirect(url_for('login'))

@admin_panel.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product_post(id):
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()

        # Check if the user has previously deleted products
        if Product.query.filter_by(deleted=True).count() > 0:
            flash("You have already deleted products!", category="warning")
        else:
            flash("Product deleted successfully!", category="success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting product: " + str(e), category="error")

    return redirect(url_for('admin_panel.products'))

def update_rate_limit(ip_address, max_calls=None, timeout=None):
    rate_limit = RateLimit.query.filter_by(ip_address=ip_address).first()

    if rate_limit:
        if max_calls is not None:
            rate_limit.max_calls = max_calls
            if max_calls < 0:
                flash("Invalid max calls value", category="error")
        if timeout is not None:
            if timeout <= 0:
                flash("Invalid timeout value", category="error")
            else:
                rate_limit.timeout = timedelta(seconds=timeout)
    else:
        rate_limit = RateLimit(ip_address=ip_address, max_calls=max_calls, timeout=datetime.now() + timedelta(seconds=timeout))

        # Check for invalid values
        if max_calls < 0:
            flash("Invalid max calls value", category="error")
        elif timeout <= 0:
            flash("Invalid timeout value", category="error")

    db.session.commit()
