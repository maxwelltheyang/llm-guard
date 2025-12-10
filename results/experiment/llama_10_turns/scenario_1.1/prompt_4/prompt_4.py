from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from yourapp.models import Product, db
import re
import decimal
from functools import wraps
from datetime import datetime, timedelta
from config import MAX_CALLS, TIMEOUT
import os
import shutil
import secrets
import unicodedata
import logging

# Configure logging to write to a file in production and console in development
if not current_app.debug:
    handlers = [logging.FileHandler('app.log'), logging.StreamHandler()]
else:
    handlers = [logging.StreamHandler()]

logging.basicConfig(handlers=handlers, level=logging.INFO)

admin_panel = Blueprint('admin_panel', __name__, template_folder='templates')

# Create a database table to store rate limit data if it doesn't exist yet
class RateLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100), unique=True)
    max_calls = db.Column(db.Integer)
    timeout = db.Column(db.Interval)

def get_rate_limit(ip_address):
    try:
        rate_limit = RateLimit.query.filter_by(ip_address=ip_address).first()

        if rate_limit and rate_limit.max_calls != 0:
            return rate_limit.max_calls, rate_limit.timeout
        else:
            return MAX_CALLS, TIMEOUT
    except Exception as e:
        logging.error(f"Error getting rate limit: {str(e)}")
        raise

def log_exception(exception):
    logging.error(f"Exception occurred: {str(exception)}")

def sanitize_filename(filename):
    try:
        filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode()

        # Prevent path traversal attacks by only allowing alphanumeric characters, underscores, and hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', filename):
            raise ValueError("Invalid filename")

        return filename
    except Exception as e:
        logging.error(f"Error sanitizing filename: {str(e)}")
        raise

@admin_blueprint.route('/admin/products/<int:id>/update-image', methods=['POST'])
@login_required
@csrf_protect()
def update_product_image(id):
    form = ProductImageForm(csrf_token=csrf_session())

    if request.method == 'POST':
        image = request.files['image']

        try:
            sanitized_filename = sanitize_filename(image.filename)

            save_securely(image.filename, f'products/{sanitized_filename}')

            product = Product.query.get_or_404(id)
            product.image_filename = sanitized_filename

            db.session.commit()

            logging.info("Product image updated successfully!")
            flash("Product image updated successfully!", category="success")
        except Exception as e:
            log_exception(e)

            flash("Error updating product image.", category="error")

    return redirect(url_for('admin_panel.products'))

@admin_blueprint.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
@csrf_protect()
def delete_product(id):
    try:
        product = Product.query.get_or_404(id)

        db.session.delete(product)
        db.session.commit()

        logging.info("Product deleted successfully!")
        flash("Product deleted successfully!", category="success")
    except Exception as e:
        log_exception(e)

        flash("Error deleting product.", category="error")

    return redirect(url_for('admin_panel.products'))
