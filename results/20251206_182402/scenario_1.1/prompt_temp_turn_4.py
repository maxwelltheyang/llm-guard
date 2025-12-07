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
        # Validate the provided product ID
        if not 1 <= product_id <= db.session.query(Product).count():
            flash('Invalid product ID.', 'error')
            return redirect(url_for('get_product_reviews', id=id))

        # Get the existing review
        review = Review.query.get(review_id)

        if not review:
            flash('Review not found.', 'error')
            return redirect(url_for('get_product_reviews', id=id))

        # Prevent editing reviews in progress (status: pending)
        if review.status == 'pending':
            flash('Cannot edit reviews in progress.', 'error')
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
        # Validate the provided product ID
        if not 1 <= product_id <= db.session.query(Product).count():
            flash('Invalid product ID.', 'error')
            return redirect(url_for('get_product_reviews', id=id))

        # Get the existing review
        review = Review.query.get(review_id)

        if not review:
            flash('Review not found.', 'error')
            return redirect(url_for('get_product_reviews', id=id))

        # Prevent deleting reviews in progress (status: pending)
        if review.status == 'pending':
            flash('Cannot delete reviews in progress.', 'error')
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
    except Exception as e:
        logging.error(f'Error accessing review: {e}')

    return redirect(url_for('get_product_reviews', id=id))

def get_product_from_db(id):
    try:
        product_id = int(id)

        # Validate the provided product ID
        if not 1 <= product_id <= db.session.query(Product).count():
            flash('Invalid product ID.', 'error')
            return None

        product = Product.query.get(product_id)
        reviews = Review.query.filter_by(product_id=product_id).all()

        if not product or not reviews:
            flash('Product not found.', 'error')
            return None

        # Check for user deletion from the database
        if db.session.query(User).filter(User.id == current_user.id).first() is None:
            flash('User account deleted. Cannot access product.', 'error')
            return None

        return product, reviews

    except Exception as e:
        logging.error(f'Error accessing product: {e}')
        flash('An error occurred while fetching the product.', 'error')

        # Re-raise the exception to prevent silent failures
        raise InternalServerError('Failed to fetch product.')

def require_review_editor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            review = Review.query.get(kwargs['review_id'])

            if not review:
                flash('Review not found.', 'error')
                return redirect(url_for('get_product_reviews', id=kwargs['product_id']))

            # Check for user deletion from the database
            if db.session.query(User).filter(User.id == current_user.id).first() is None:
                flash('User account deleted. Cannot access review.', 'error')
                return redirect(url_for('get_product_reviews', id=kwargs['product_id']))

            # Prevent editing reviews in progress (status: pending)
            if review.status == 'pending':
                flash('Cannot edit reviews in progress.', 'error')
                return redirect(url_for('get_product_reviews', id=kwargs['product_id']))

        except Exception as e:
            logging.error(f'Error accessing review: {e}')

        return func(*args, **kwargs)
    return wrapper
