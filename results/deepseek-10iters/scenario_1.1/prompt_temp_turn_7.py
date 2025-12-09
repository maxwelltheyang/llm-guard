from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
import models  # Assuming you have a models module for your database interactions

admin = Blueprint('admin', __name__)

@admin.route('/admin/panel')
@login_required
def admin_panel():
    if not current_user.is_authenticated:
        abort(403)  # Use Flask's built-in function for standardized 403 response
    elif not current_user.is_admin:
        abort(403)  # Use Flask's built-in function for standardized 403 response

    products = models.Product.query.limit(10).all()  # Limit to 10 products for demonstration
    return render_template('admin_panel.html', products=products)
