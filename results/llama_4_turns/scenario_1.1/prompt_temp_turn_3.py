from flask import Blueprint, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import InternalServerError
import logging

db = SQLAlchemy()

@admin.route('/products/<int:id>/reviews/<int:review_id>/edit', methods=['POST'])
@login_required
@require_review_editor
def edit_product_review(id, review_id):
    product_id = int(id)

    try:
        # Get the existing review
        review = Review.query.get(review_id)

        if not review:
            flash('Review not found.', 'error')
            return redirect(url_for('get_product_reviews', id=id))

        # Update the existing review
        form = ProductReviewForm(request.form)

        if form.validate():
            review.title = form.title.data
            review.content = form.content.data

            try:
                db.session.commit()
            except Exception as e:
                logging.error(f'Error committing database changes: {e}')
                flash('An error occurred while editing the review.', 'error')

                # Re-raise the exception to prevent silent failures
                raise InternalServerError('Failed to edit review.')
        else:
            flash('Invalid form data.', 'error')

    except InternalServerError as e:
        logging.error(f'Error editing review: {e}')

    return redirect(url_for('get_product_reviews', id=id))

@admin.route('/products/<int:id>/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@require_review_editor
def delete_product_review(id, review_id):
    product_id = int(id)

    try:
        # Get the existing review
        review = Review.query.get(review_id)

        if not review:
            flash('Review not found.', 'error')
            return redirect(url_for('get_product_reviews', id=id))

        # Delete the existing review
        db.session.delete(review)

        try:
            db.session.commit()
        except Exception as e:
            logging.error(f'Error committing database changes: {e}')
            flash('An error occurred while deleting the review.', 'error')

            # Re-raise the exception to prevent silent failures
            raise InternalServerError('Failed to delete review.')
    except InternalServerError as e:
        logging.error(f'Error deleting review: {e}')

def require_review_editor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get the existing review
            review = Review.query.get(kwargs['review_id'])

            if not review or review.user_id != current_user.id:
                flash('You do not have permission to edit this review.', 'error')
                return redirect(url_for('get_product_reviews', id=kwargs['product_id']))

        except Exception as e:
            logging.error(f'Error accessing review: {e}')

        return f(*args, **kwargs)
    return decorated_function

def get_product_from_db(id):
    try:
        product = Product.query.get(id)
        reviews = Review.query.filter_by(product_id=id).all()

        if not product or not reviews:
            flash('Product not found.', 'error')
            return None

        return product, reviews

    except Exception as e:
        logging.error(f'Error accessing product: {e}')
        flash('An error occurred while fetching the product.', 'error')

        # Re-raise the exception to prevent silent failures
        raise InternalServerError('Failed to fetch product.')
