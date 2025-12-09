from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3

app = Flask(__name__)

# Database setup using SQLAlchemy for better security and practices
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)

engine = create_engine('sqlite:///products.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db_connection():
    return Session()

@app.route('/products', methods=['GET'])
def get_products():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    products = []
    if search_query:
        query = "SELECT * FROM products WHERE name LIKE :search OR description LIKE :search"
        cursor = conn.execute(query, {'search': '%' + search_query + '%'})
        products = [dict(row) for row in cursor.fetchall()]
    else:
        cursor = conn.execute("SELECT * FROM products")
        products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=False)
