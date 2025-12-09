import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Ensure secret key is set securely
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret')  # Replace 'default_secret' with a secure, random key in production

# Configure the database connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure session security
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ['true', '1', 't']  # Set to True in production
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize the database
db = SQLAlchemy(app)

# Define a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# Define an AuditLog model
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    previous_score = db.Column(db.Integer, nullable=False)
    new_score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

with app.app_context():
    db.create_all()

# Ensure that the admin password hash is securely set
hashed_admin_password = os.getenv(
    'ADMIN_PASSWORD_HASH',
    generate_password_hash('securepassword')  # Change 'securepassword' to the actual secure password
)

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == os.getenv('ADMIN_USERNAME', 'admin') and check_password_hash(hashed_admin_password, password):
            session['logged_in'] = True
            session['username'] = username  # Store admin username in session
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
                previous_score = user.score
                user.score = new_score
                db.session.commit()
                # Log the update action
                audit_log = AuditLog(admin_username=session['username'], user_id=user_id,
                                     previous_score=previous_score, new_score=new_score)
                db.session.add(audit_log)
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
    # Ensure that debug mode is controlled securely
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
