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
if os.environ.get('FLASK_ENV') == 'production':
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    except KeyError as e:
        flash(f"Error: Database URL not provided - {e}")
        return "Error: Database URL not provided"
else:
    # For development, generate a secret key securely
    import secrets
    secure_secret_key = secrets.token_hex(16)
    app.config['SECRET_KEY'] = secure_secret_key
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    except KeyError as e:
        flash(f"Error: Database URI not provided - {e}")
        return "Error: Database URI not provided"

# Use environment variables for sensitive data
app.config.from_envvar('APP_CONFIG_FILE')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def is_admin(self):
        return self.role.name == 'admin'

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    description = db.Column(db.Text)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(128))
    image_data = db.Column(db.LargeBinary())

@app.route('/view/<int:image_id>')
def view_image(image_id):
    if not g.current_user:
        flash('Access denied')
        return redirect(url_for('index'))

    image = Image.query.get_or_404(image_id)

    if g.current_user.id == image.author_id or (g.current_user.is_admin() and image.author.is_admin()):
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
