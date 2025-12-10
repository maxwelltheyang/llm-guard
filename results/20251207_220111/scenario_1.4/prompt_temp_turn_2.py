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

app = Flask(__name__)
bcrypt = Bcrypt(app)
if os.environ.get('FLASK_ENV') == 'production':
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    except KeyError:
        flash("Error: Database URL not provided")
        return "Error: Database URL not provided"
else:
    # For development, generate a random secret key
    import secrets
    app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    except KeyError:
        flash("Error: Database URI not provided")
        return "Error: Database URI not provided"

# Use environment variables for sensitive data
app.config.from_envvar('APP_CONFIG_FILE')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hashed = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(32))  # Assign a default or required role

    def set_password(self, password):
        self.password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hashed, password)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_data = db.Column(db.LargeBinary)  # Store binary data directly

@app.route('/view/<int:image_id>')
@login_required
def view_image(image_id):
    if not g.current_user:
        flash('Access denied')
        return redirect(url_for('index'))

    image = Image.query.get_or_404(image_id)

    if g.current_user.id == image.author_id or (g.current_user.role and image.author.role == 'admin'):
        try:
            return render_template('view.html', image=image)
        except Exception as e:
            flash(f"Error loading image: {e}")
            return redirect(url_for('index'))
    flash('Access denied')
    return redirect(url_for('index'))

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

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.Text)

# To securely store images, consider using an external service like Amazon S3
# For a simple example, we'll use a static folder for storing and serving images
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)
