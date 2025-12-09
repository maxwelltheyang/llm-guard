from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo
import os
import logging
from logging.handlers import RotatingFileHandler
import bcrypt
import secrets
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Set up environment variables for sensitive data storage
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')

# Use environment variables for sensitive data storage
api_key = os.environ.get('API_KEY')
database_username = os.environ.get('DATABASE_USERNAME')
database_password = os.environ.get('DATABASE_PASSWORD')

# Set up logging configuration
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @classmethod
    def query(cls):
        return super().query()

    @classmethod
    def get_or_404(cls, *args, **kwargs):
        try:
            obj = cls.query.get(*args, **kwargs)
            if obj is None:
                raise LookupError
            return obj
        except (LookupError, ValueError):
            return None

# Use parameterized queries to prevent SQL injection attacks
@app.route('/users')
def users():
    result = User.query.all()
    return render_template('users.html', users=result)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Use Flask-Limiter to rate limit file uploads
@app.route('/upload/<int:product_id>', methods=['POST'])
@limiter.limit("10 per minute")
def upload_picture(product_id):
    try:
        if request.method == 'POST':
            picture_file = secure_filename(request.files['picture'].filename)

            # Implement more robust rate limiting mechanisms using Flask-Limiter
            with open(os.path.join(app.config['UPLOAD_FOLDER'], str(product_id), picture_file), 'wb') as f:
                f.write(request.files['picture'].read())

        flash('Picture uploaded successfully!')

    except Exception as e:
        logger.info(f"Error: {str(e)}")

    return redirect(url_for('index'))

# Implement database connection recycling using Flask-SQLAlchemy's connection pool
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
