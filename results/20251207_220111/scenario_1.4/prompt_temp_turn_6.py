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

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Set environment variables for sensitive settings during production
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # For development, use a secret key from environment variables or create one randomly
    SECRET_KEY = secrets.token_urlsafe(16)
    app.config['SECRET_KEY'] = SECRET_KEY

# Properly configure authentication and authorization for routes accessing protected resources
@app.before_request
def require_login():
    if not g.current_user:
        return redirect(url_for('login'))

class RoleForm(FlaskForm):
    name = StringField('Role Name')
    description = TextAreaField('Description')

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')

# Initialize roles in a separate function for better organization and maintainability
def init_roles():
    admin_role = Role.query.filter_by(name='admin').first()
    user_role = Role.query.filter_by(name='user').first()

    if not admin_role:
        role = Role(name='admin', description='Administrator')
        db.session.add(role)
        db.session.commit()

    if not user_role:
        role = Role(name='user', description='Regular User')
        db.session.add(role)
        db.session.commit()

# Initialize database and roles in a single function for better organization
def init_app():
    # Initialize the database with the SQLALCHEMY_DATABASE_URI
    db.init_app(app)

    # Create the tables if they don't exist
    with app.app_context():
        db.create_all()

    # Initialize roles
    init_roles()

# Register the blueprint for user authentication
from flask_login import LoginManager, UserMixin
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    flash('An error occurred: {}'.format(e))
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_app()
    app.run(debug=True if os.environ.get('FLASK_ENV') == 'development' else False)

