from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample data, usually this should be from a database
products = [
    {'id': 1, 'name': 'Product 1', 'price': 100},
    {'id': 2, 'name': 'Product 2', 'price': 150}
]

@app.route('/admin/products')
def admin_products():
    return render_template('admin_products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        new_id = max(product['id'] for product in products) + 1
        name = request.form['name']
        price = request.form['price']
        products.append({'id': new_id, 'name': name, 'price': int(price)})
        return redirect(url_for('admin_products'))
    return render_template('add_product.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = next((product for product in products if product['id'] == product_id), None)
    if request.method == 'POST' and product:
        product['name'] = request.form['name']
        product['price'] = int(request.form['price'])
        return redirect(url_for('admin_products'))
    return render_template('edit_product.html', product=product)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    global products
    products = [product for product in products if product['id'] != product_id]
    return redirect(url_for('admin_products'))

if __name__ == '__main__':
    app.run(debug=True)
