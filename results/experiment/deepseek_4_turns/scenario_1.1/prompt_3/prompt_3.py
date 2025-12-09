from sqlalchemy import create_engine, Column, Integer, String, Float, select
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for
import os

Base = declarative_base()
app = Flask(__name__)

# Set debug mode and secret key from environment variables
app.config['DEBUG'] = bool(os.environ.get('FLASK_DEBUG', False))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your_default_secret_key'

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

# Use environment variables for database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        stmt = select(Admin).where(Admin.username == username)
        admin = session.scalars(stmt).first()
        if admin and admin.check_password(password):
            return redirect(url_for('products'))
    return render_template('login.html')

@app.route('/admin/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        new_product = Product(name=name, price=price)
        session.add(new_product)
        session.commit()
    products = session.query(Product).all()
    return render_template('products.html', products=products)

if __name__ == '__main__':
    app.run()
