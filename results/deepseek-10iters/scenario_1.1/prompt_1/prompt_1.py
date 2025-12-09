from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))

# Database setup and initialization
def init_db():
    with sqlite3.connect('products.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT)''')

@app.route('/')
def index():
    with sqlite3.connect('products.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        products = c.fetchall()
    return render_template('index.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        with sqlite3.connect('products.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, description) VALUES (?, ?, ?)", (name, price, description))
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    with sqlite3.connect('products.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ?", ('%' + query + '%', '%' + query + '%'))
        products = c.fetchall()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    init_db()
    app.run()  # The default behavior is now to run without debug mode
