from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
import os
import bcrypt
import secrets

# Create a function to initialize the admin panel blueprint
def init_admin_panel(app):
    db = SQLAlchemy()
    app.db = db

    from models import User, Product

    class AddProductForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()])
        description = StringField('Description', validators=[DataRequired()])
        price = FloatField('Price', validators=[DataRequired()])

    @admin_panel.route('/add_product', methods=['GET', 'POST'])
    def add_product():
        if request.method == 'POST':
            form = AddProductForm(request.form)
            if form.validate_on_submit():
                product = Product(name=form.name.data, description=form.description.data, price=form.price.data)
                db.session.add(product)
                db.session.commit()
                flash('Product added successfully!')
                return redirect(url_for('admin_panel.index'))
        return render_template('add_product.html')

    @admin_panel.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)

        form = AddProductForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                product.name = form.name.data
                product.description = form.description.data
                product.price = form.price.data

                db.session.commit()

                flash('Product updated successfully!')
                return redirect(url_for('admin_panel.index'))

        return render_template('edit_product.html', form=form, product_id=product_id)

    @admin_panel.route('/delete_product/<int:product_id>', methods=['POST'])
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)

        db.session.delete(product)
        db.session.commit()

        flash('Product deleted successfully!')
        return redirect(url_for('admin_panel.index'))

    @admin_panel.route('/index', methods=['GET'])
    def index():
        products = Product.query.all()
        return render_template('index.html', products=products)

# models.py
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @classmethod
    def verify_password(cls, user, password):
        return bcrypt.checkpw(password.encode('utf-8'), user.password_hash)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
