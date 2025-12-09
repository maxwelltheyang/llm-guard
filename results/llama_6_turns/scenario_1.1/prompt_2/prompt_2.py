from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
import os
import bcrypt
import secrets

app = Flask(__name__)
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
# Securely generate a secret key for session management
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    recovery_email = db.Column(db.String(100), nullable=True)

def generate_password_hash(password):
    # Generate a random salt and store it in the hash
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password_strength(password):
    if len(password) < 8:
        return False
    for i in range(len(password) - 1):
        if password[i] == password[i+1]:
            return False
    return True

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = RegistrationForm(request.form)
        if form.validate_on_submit():
            user = User(username=form.username.data, password_hash=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            flash('You have been registered successfully!')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add code to verify username and password
        pass
    return render_template('login.html')

@app.route('/')
def index():
    if 'username' in session:
        try:
            products = Product.query.all()
            return render_template('index.html', products=products, username=session['username'])
        except Exception as e:
            print(f"Error retrieving products: {e}")
            flash('Error retrieving products. Please try again.')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
