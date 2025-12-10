from flask import Flask, request, render_template, url_for, redirect, abort, session, g
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import logging.config
import boto3
from botocore.exceptions import NoCredentialsError, ClientError, MissingLoginTokenError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
from cryptography.fernet import Fernet
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different username.')

class EditCaptionForm(FlaskForm):
    new_caption = StringField('New Caption', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE')
db = SQLAlchemy(app)
# Load sensitive data from environment variables
password_hashing_key = os.environ.get('PASSWORD_HASHING_KEY')

try:
    # Load logging configuration from file. Ensure this file exists in the correct location.
    logging.config.fileConfig('logging.conf')
except FileNotFoundError as e:
    logging.error(f"Logging configuration file not found: {e}")
except Exception as e:
    logging.error(f"Error loading logging configuration: {e}")
else:
    print("Logging configuration loaded successfully.")

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role = db.Column(db.String(50), default='user')  # Set a default value for the 'role' attribute
    images = relationship('Image', backref='user')

# Protect the edit-caption route with login_required decorator and use current_user.id
from flask_login import LoginManager, UserMixin, current_user
login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/edit-caption', methods=['GET', 'POST'])
@login_required
def edit_caption():
    form = EditCaptionForm()
    if request.method == 'POST':
        new_image = Image(caption=form.new_caption.data, image_url=request.form['image_url'], user_id=current_user.id)
        db.session.add(new_image)
        db.session.commit()
        return "Image updated successfully!"
    images = Image.query.filter(Image.user_id == current_user.id).all()  # Filter by user's images
    return render_template('edit-caption.html', images=images, form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'], salt_length=None, key=password_hashing_key)
        try:
            new_user = User(username=request.form['username'], role='user', password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return 'User created successfully!'
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return "Error creating user. Please try again."
    form = RegistrationForm()
    return render_template('register.html', form=form)

def generate_password_hash(password, salt_length=None, key=password_hashing_key):
    # This is a simplified example of password hashing and should not be used in production.
    # A secure password hashing library such as Argon2 or PBKDF2 should be used instead.
    import hashlib
    return hashlib.sha256(f"{password}{key}".encode()).hexdigest()

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
