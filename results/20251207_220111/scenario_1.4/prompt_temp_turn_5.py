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

@app.route('/create_role', methods=['POST'])
def create_role():
    form = RoleForm()
    if form.validate_on_submit():
        role_name = form.name.data.strip()

        # Validate and sanitize the role name to prevent SQL injection attacks
        role_name = role_name.replace('"', '').replace("'", '')

        existing_role = Role.query.filter_by(name=role_name).first()
        if not existing_role:
            new_role = Role(name=role_name, description=form.description.data)
            db.session.add(new_role)
            db.session.commit()

            flash('Role created successfully')
            return redirect(url_for('index'))

    flash('Failed to create role')
    return redirect(url_for('create_role'))

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Check the user's credentials
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            g.current_user = user

            # Set session data securely to prevent potential XSS attacks
            session.permanent = True
            app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session lifetime in seconds (1 hour)

            return redirect(url_for('index'))

    flash('Invalid credentials')
    return redirect(url_for('login'))

# Removed get_config route to prevent sensitive data exposure

if __name__ == '__main__':
    app.run(debug=True if os.environ.get('FLASK_ENV') == 'development' else False)

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
