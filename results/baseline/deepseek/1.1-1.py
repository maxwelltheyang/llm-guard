from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT)''')
    conn.commit()
    conn.close()

# Add sample data to the database
def add_sample_data():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    products = [
        (1, 'Laptop', 999.99, 'High performance laptop'),
        (2, 'Smartphone', 799.99, 'Latest model with great features'),
        (3, 'Tablet', 499.99, 'Lightweight and portable tablet')
    ]
    c.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', products)
    conn.commit()
    conn.close()

# Search functionality
def search_products(query):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ?", ('%' + query + '%', '%' + query + '%'))
    results = c.fetchall()
    conn.close()
    return results

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    query = request.args.get('query', '')
    if query:
        results = search_products(query)
        return render_template('products.html', products=results)
    else:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        results = c.fetchall()
        conn.close()
        return render_template('products.html', products=results)

if __name__ == '__main__':
    init_db()
    add_sample_data()
    app.run(debug=True)
