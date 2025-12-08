from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, UserMixin
from .models import Product, Review, db
from wtforms import Form, StringField, validators, FileField, TextAreaField
import logging
from functools import wraps

admin = Blueprint('admin', __name__)

class AdminProductForm(Form):
    name = StringField('Name')
    description = StringField('Description')
    price = FloatField('Price')

def require_admin_role(f):
    """
    Requires the current user to have the 'admin' role and sufficient permissions for administrative actions.

    :param f: The function to decorate
    :return: A decorated function that checks for admin role and permissions
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('admin'):
            flash('You do not have permission to access this feature.', 'error')
            return redirect(url_for('index'))

        # Additional permission checks can be added here based on the user's role and attributes
        # For example:
        # if not current_user.has_permission('delete_products'):
        #     flash('You do not have permission to delete products.', 'error')
        #     return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function

def get_product_from_db(product_id):
    product = Product.query.get(product_id)

    if product:
        reviews = Review.query.filter_by(product_id=product.id).all()

        # Check if at least one review is present for the product
        if not reviews:
            flash(f'There are no reviews for {product.name}.', 'info')

        return product, reviews
    else:
        flash('Product does not exist.', 'error')

    return None, []

class ProductReviewForm(Form):
    title = StringField('Title', [validators.DataRequired(), validators.Length(min=1, max=50)])
    content = TextAreaField('Content', [validators.DataRequired(), validators.Length(min=10, max=500)])

@admin.route('/products/<int:id>/reviews', methods=['GET'])
@login_required
def get_product_reviews(id):
    product, reviews = get_product_from_db(id)

    if not product:
        return redirect(url_for('index'))

    return render_template('product_reviews.html', reviews=reviews, product=product)

@admin.route('/products/<int:id>/reviews', methods=['POST'])
@login_required
def post_product_review(id):
    try:
        product = get_product_from_db(id)

        if not product:
            return redirect(url_for('index'))

        form = ProductReviewForm(request.form)

        if form.validate():
            # Check if the current user has already reviewed the product
            existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product.id).first()

            if existing_review:
                flash(f'You have already reviewed {product.name}.', 'error')
                return redirect(url_for('get_product_reviews', id=id))

            new_review = Review(title=form.title.data, content=form.content.data, user_id=current_user.id, product_id=product.id)
            db.session.add(new_review)

            try:
                db.session.commit()
            except Exception as e:
                logging.error(f'Error committing database changes: {e}')
                flash('An error occurred while posting the review.', 'error')
                return redirect(url_for('get_product_reviews', id=id))

            flash('Review posted successfully', 'success')
        else:
            flash('Invalid form data.', 'error')

    except ValueError:
        flash('Invalid product ID.', 'error')

    return redirect(url_for('get_product_reviews', id=id))

if __name__ == '__main__':
    admin.init_app(app)

class Product(db.Model):
    # ...

class Review(db.Model):
    # ...
