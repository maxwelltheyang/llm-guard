from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG'] = False if app.config.get('FLASK_ENV') == 'production' else True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['WTF_CSRF_TIME_LIMIT'] = 300

# Create a secure logger to prevent sensitive data exposure
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Set up file-based logging for production environments
if app.config.get('FLASK_ENV') == 'production':
    handler = logging.FileHandler('errors.log')
else:
    handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    reset_token = db.Column(db.String(32))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(128), nullable=False)

@app.route('/admin')
def admin():
    if 'admin' in session:
        return render_template('admin.html')

# Validate user IDs to prevent SQL injection attacks
def validate_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(kwargs['id'], int) or kwargs['id'] < 1:
            logger.error("Invalid user ID provided")
            return "Error: Invalid user ID"
        return func(*args, **kwargs)
    return wrapper

@app.route('/delete-post', methods=['POST'])
@validate_id
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('admin'))
    else:
        logger.error("Post not found with ID {}".format(id))
        return "Error: Post not found"

@app.route('/delete-comment', methods=['POST'])
@validate_id
def delete_comment(id):
    comment = Comment.query.get(id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('admin'))
    else:
        logger.error("Comment not found with ID {}".format(id))
        return "Error: Comment not found"

@app.route('/update-profile', methods=['POST'])
def update_profile():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        if user:
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            return redirect(url_for('profile'))
    return "Form is invalid"

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data,
                        password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    logger.error("Form is invalid")
    return "Form is invalid"

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            logger.error("Invalid username or password")
            return "Error: Invalid username or password"
    return "Form is invalid"

@app.route('/logout')
def logout():
    del session['user_id']
    return redirect(url_for('login'))

class UpdateProfileForm(FlaskForm):
    new_username = StringField('New Username', validators=[DataRequired()])
    new_email = StringField('New Email', validators=[DataRequired(), Email()])

@app.route('/update-profile', methods=['POST'])
def update_profile_form():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        if user:
            user.username = form.new_username.data
            user.email = form.new_email.data
            db.session.commit()
            return redirect(url_for('profile'))
    logger.error("Form is invalid")
    return "Form is invalid"
