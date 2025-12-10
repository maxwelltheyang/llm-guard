from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import BCRYPT
from secrets import token_urlsafe
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from flask_wtf import FlaskForm
import jwt

app = Flask(__name__)
config = Config
if not hasattr(config, 'DEBUG'):
    raise Exception("Production mode should be enabled for security reasons")
else:
    app.config.from_object(config)

db = SQLAlchemy(app)
bcrypt = BCRYPT()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class AdminForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])

@app.before_request
def require_login():
    if request.path.startswith('/admin/'):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.query.get(user_id)
            if user and bcrypt.check_password_hash(user.password, payload['password']):
                session['user_id'] = user_id
            else:
                return jsonify({'error': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Session expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        payload = {'user_id': user.id, 'password': password}
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', category='success')
    return redirect(url_for('index'))

@app.route('/admin/products', methods=['GET', 'POST'])
@csrf.exempt()
def admin_products():
    if request.method == 'POST':
        form = AdminForm(request.form, csrf_enabled=False)
        if form.validate_on_submit():
            product = Product(name=form.name.data, description=form.description.data, price=form.price.data)
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', category='success')
            return redirect(url_for('admin_products'))
    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@app.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@csrf.exempt()
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        form = AdminForm(request.form, obj=product, csrf_enabled=False)
        if form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.price = form.price.data
            db.session.commit()
            flash('Product updated successfully!', category='success')
            return redirect(url_for('admin_products'))
    form = AdminForm(obj=product)
    return render_template('edit_product.html', form=form)

@app.route('/admin/products/<int:id>/delete', methods=['POST'])
@csrf.exempt()
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', category='success')
    return redirect(url_for('admin_products'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host=os.getenv("HOST", "localhost"), port=int(os.getenv("PORT", 5000)), debug=False)
