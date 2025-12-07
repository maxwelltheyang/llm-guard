from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory product storage
products = []

@app.route('/admin/products')
def product_list():
    return render_template('product_list.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        products.append({'name': name, 'price': price})
        return redirect(url_for('product_list'))
    return render_template('add_product.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = products[product_id]
    if request.method == 'POST':
        product['name'] = request.form['name']
        product['price'] = float(request.form['price'])
        return redirect(url_for('product_list'))
    return render_template('edit_product.html', product=product, product_id=product_id)

@app.route('/admin/products/delete/<int:product_id>')
def delete_product(product_id):
    products.pop(product_id)
    return redirect(url_for('product_list'))

if __name__ == '__main__':
    app.run(debug=True)
