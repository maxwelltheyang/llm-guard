from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for demonstration purposes
products = []

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    product = {'id': len(products) + 1, 'name': name, 'price': price, 'stock': stock}
    products.append(product)
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        product = {'id': id, 'name': name, 'price': price, 'stock': stock}
        for i in range(len(products)):
            if products[i]['id'] == id:
                products[i] = product
                break
        return redirect(url_for('index'))
    else:
        product = next((p for p in products if p['id'] == id), None)
        if product is None:
            return "Product not found", 404
        return render_template('edit.html', product=product)

@app.route('/delete/<int:id>')
def delete(id):
    global products
    products = [p for p in products if p['id'] != id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
