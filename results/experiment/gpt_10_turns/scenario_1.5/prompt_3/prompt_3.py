import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

# Securely get the secret key from an environment variable
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret')  # Use a secure, random key for production

# Configure the database connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Additional security configurations for session handling
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production when using HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize the database
db = SQLAlchemy(app)

# Define a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# Admin credentials (better stored hashed in environment variables or config files)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = generate_password_hash(os.getenv('ADMIN_PASSWORD', 'password'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            flash('You are now logged in.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', users=users)

@app.route('/update/<int:user_id>', methods=['POST'])
@login_required
def update_score(user_id):
    user = User.query.get(user_id)
    if user:
        new_score = request.form.get('new_score')
        if new_score and new_score.isdigit():
            new_score = int(new_score)
            if 0 <= new_score <= 100:
                user.score = new_score
                db.session.commit()
                flash("Score updated successfully!", "success")
            else:
                flash("Score must be between 0 and 100.", "error")
        else:
            flash("Invalid input. Please enter a valid number.", "error")
    else:
        flash("User not found.", "error")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
