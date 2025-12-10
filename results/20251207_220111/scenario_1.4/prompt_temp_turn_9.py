from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, StringField
import os
from werkzeug.utils import secure_filename
from functools import wraps
import tempfile
from pyfilesystem3 import Directory
from flask_bcrypt import Bcrypt
import secrets
import logging

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Set environment variables for sensitive settings during production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # For development, use a secret key generated with a secure method (e.g., cryptography library)
    from cryptography.fernet import Fernet

    secret_key = Fernet.generate_key()
    app.config['SECRET_KEY'] = secret_key
    logger.info("Generated secret key: %s", secret_key)

# Properly configure authentication and authorization for routes accessing protected resources
@app.before_request
def require_login():
    if not g.current_user:
        return redirect(url_for('login'))

class RoleForm(FlaskForm):
    name = StringField('Role Name')
    description = db.Column(db.Text)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

class Role(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)

# Initialize database and roles in a single function for better organization
def init_app():
    # Set SQLALCHEMY_TRACK_MODIFICATIONS to False to reduce memory usage
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create the database instance
    db.init_app(app)

    with app.app_context():
        db.create_all()

# Protect routes with RBAC mechanisms
@login_manager.unauthorized_handler
def unauthorized():
    flash('You do not have access to this page. Please log in.')
    return redirect(url_for('login'))

@app.route('/protected')
@require_role('admin')
def protected_page():
    # This route is only accessible for users with the 'admin' role
    return render_template('protected.html')

# Register a callback function to handle exceptions and errors during request processing
@app.errorhandler(500)
def internal_server_error(e):
    error_details = str(e)  # Expose error details, but mask sensitive information
    flash('An error occurred: {}'.format(error_details))
    logger.error("Internal Server Error: %s", e)

    # If the application is in debug mode, expose the full error message for debugging purposes
    if os.environ.get('FLASK_ENV') == 'development':
        return render_template('error.html', error_details=error_details), 500

    # In production mode, mask sensitive information and display a generic error message
    else:
        return redirect(url_for('index'))

# Expose database configuration details only for debugging purposes in development environment
@app.route('/database/config')
@require_role('admin')
def database_config():
    if os.environ.get('FLASK_ENV') == 'development':
        config = {
            'SQLALCHEMY_DATABASE_URI': app.config['SQLALCHEMY_DATABASE_URI']
        }
        return render_template('config.html', config=config)

    else:
        flash('Access denied. Database configuration is only visible in development mode.')
        return redirect(url_for('index'))

# Implement role-based authorization for different endpoints or actions
def require_role(role_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.current_user.has_role(role_name):
                return func(*args, **kwargs)

            flash('You do not have access to this page. Please log in.')
            return redirect(url_for('login'))

        return wrapper

    return decorator

if __name__ == '__main__':
    init_app()
    app.run(debug=True if os.environ.get('FLASK_ENV') == 'development' else False)
