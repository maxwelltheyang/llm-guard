from flask import Flask, request, jsonify
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

# Database setup using SQLAlchemy for better security and practices
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)

# Use environment variables for database connection string in a production environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///products.db')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db_connection():
    try:
        conn = Session()
        return conn
    except Exception as e:
        print("Error connecting to the database:", str(e))
        return None

@app.route('/products', methods=['GET'])
def get_products():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    products = []
    try:
        cursor = conn.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
        products = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print("Database error:", str(e))
        return jsonify({"error": "An error occurred while querying the database"}), 500
    finally:
        conn.close()

    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=False)
