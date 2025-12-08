from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Product model (for simplicity, we assume it's a class with id and name attributes)
class Product:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# In-memory products list (replace with database in real app)
products = [
    Product(1, 'Product 1'),
    Product(2, 'Product 2')
]

# Admin panel route
@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
def admin_products():
    if current_user.is_admin:
        # Handle form submission (adding or editing product)
        if request.method == 'POST':
            if request.form['action'] == 'add':
                new_product = Product(len(products) + 1, request.form['name'])
                products.append(new_product)
            elif request.form['action'] == 'edit':
                product_id = int(request.form['id'])
                for product in products:
                    if product.id == product_id:
                        product.name = request.form['name']
        # Render admin panel template with products list
        return render_template('admin_products.html', products=products)
    else:
        return redirect(url_for('login'))

# Delete product route (using GET method for simplicity, but in real app use POST and handle form submission)
@app.route('/admin/products/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    if current_user.is_admin:
        for i, product in enumerate(products):
            if product.id == product_id:
                products.pop(i)
        return redirect(url_for('admin_products'))
    else:
        return redirect(url_for('login'))

# Run the application (in real app use a WSGI server like Gunicorn or mod_wsgi)
if __name__ == '__main__':
    app.run(debug=True)
