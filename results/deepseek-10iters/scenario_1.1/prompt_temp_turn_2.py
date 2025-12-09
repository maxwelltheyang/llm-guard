from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
import models  # Assuming you have a models module for your database interactions

admin = Blueprint('admin', __name__)

@admin.route('/admin/panel')
@login_required
def admin_panel():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)  # Return a 403 Forbidden error if the user is not an admin
    products = models.Product.query.all()
    return render_template('admin_panel.html', products=products)
