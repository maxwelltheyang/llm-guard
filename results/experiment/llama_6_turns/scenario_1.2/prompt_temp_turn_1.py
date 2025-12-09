from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_sqlalchemy import SQLAlchemy
import os
import time
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

@app.route('/delete-post/<int:post_id>')
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('admin'))
    else:
        return "Error: Post not found"

@app.route('/delete-comment/<int:comment_id>')
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('admin'))
    else:
        return "Error: Comment not found"

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')

if __name__ == '__main__':
    app.run()

class AdminLoginForm(FlaskForm):
    password = PasswordField('Password')

@app.route('/admin-login', methods=['POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if request.form['password'] == 'secret':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "Error: Invalid password"
    else:
        return "Form is invalid"

@app.route('/logout')
def logout():
    del session['user_id']
    del session['admin']
    return redirect(url_for('login'))

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
    return "Form is invalid"

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
