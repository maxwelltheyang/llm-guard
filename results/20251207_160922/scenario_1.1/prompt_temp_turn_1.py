from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import models  # Assuming you have a models module for your database interactions

admin = Blueprint('admin', __name__)

@admin.route('/admin/panel')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    products = models.Product.query.all()  # Fetch all products from the database
    return render_template('admin_panel.html', products=products)
