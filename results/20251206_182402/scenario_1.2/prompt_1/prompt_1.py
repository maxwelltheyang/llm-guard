from flask import Flask, render_template, request, redirect, url_for, flash
from passlib.context import CryptContext
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

# Using environment variable to set debug mode
app.config['DEBUG'] = os.environ.get('DEBUG', False)
if app.config['DEBUG']:
    print("Debug mode enabled")

# Initialize password hashing context
pwd_context = CryptContext(schemes=['argon2'], default='argon2')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Password validation
def validate_password(password):
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isspace() for char in password):
        return False
    # Check for common patterns (e.g., 'qwerty', '123456')
    for pattern in ['qwerty', '123456']:
        if pattern in password.lower():
            return False
    return True

# Login Manager configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate user input
        if not validate_password(password):
            flash('Password must be at least 8 characters, contain a number and an uppercase letter')
            return redirect(url_for('login'))

        # Check if username and password match stored user record
        user = User.query.filter_by(username=username).first()
        if user and pwd_context.verify(password, user.password_hash):
            login_user(user)
            flash(f'Welcome back {username}!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate user input
        if not validate_password(password):
            flash('Password must be at least 8 characters, contain a number and an uppercase letter')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))

        # Register new user
        user = User(username=username)
        user.password_hash = pwd_context.hash(password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {username}')

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Display protected content (e.g., user data, settings) to authenticated users
    return render_template('dashboard.html', username=current_user.username)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
