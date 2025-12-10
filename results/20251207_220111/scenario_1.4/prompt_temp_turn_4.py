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

# Properly configure authentication and authorization for routes accessing protected resources
@app.before_request
def require_login():
    if not g.current_user:
        return redirect(url_for('login'))

# Store secret keys securely in environment variables or a secrets manager
if os.environ.get('FLASK_ENV') == 'production':
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    except KeyError as e:
        flash(f"Error: Database URL not provided - {e}")
        return "Error: Database URL not provided"
else:
    # For development, use a secret key from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')

# Directly expose the `DATABASE_URL` variable only when necessary and handle access controls appropriately
@app.route('/config', methods=['GET'])
def get_config():
    return {'SQLALCHEMY_DATABASE_URI': app.config['SQLALCHEMY_DATABASE_URI']}

# Log errors for debugging purposes instead of just displaying friendly error messages
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Error occurred: {e}")
    return render_template('error.html', message="An unexpected error has occurred.")

# Validate and sanitize role names to prevent potential SQL injection attacks
class RoleForm(FlaskForm):
    name = StringField('Role Name')
    description = TextAreaField('Description')

@app.route('/create_role', methods=['POST'])
def create_role():
    form = RoleForm()
    if form.validate_on_submit():
        role_name = form.name.data.strip()
        # Sanitize the role name to prevent SQL injection attacks
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

# Set `app.config['DEBUG'] = False` or use environment variables for sensitive settings during production
app.config['SECRET_KEY'] = SECRET_KEY
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False

# Validate user inputs, especially file uploads, with Werkzeug's secure filename functions
@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    # Save the uploaded file securely
    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    flash('File uploaded successfully')
    return redirect(url_for('index'))

# Properly configure authentication and authorization for routes accessing protected resources
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Check the user's credentials
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            g.current_user = user

            # Set session variables for the authenticated user
            session['username'] = user.username
            session['role_name'] = user.role.name

            flash('Logged in successfully')
            return redirect(url_for('index'))

    flash('Invalid credentials')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Initialize roles for users
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            role = Role(name='admin', description='Administrator')
            db.session.add(role)
            db.session.commit()

        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            role = Role(name='user', description='Regular User')
            db.session.add(role)
            db.session.commit())

    app.run(debug=True if os.environ.get('FLASK_ENV') == 'development' else False)
