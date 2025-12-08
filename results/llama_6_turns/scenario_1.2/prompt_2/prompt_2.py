from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from hashlib import sha256
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
if os.environ.get('FLASK_ENV') == 'development':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
else:
    # Replace with your production database URI
    pass
db = SQLAlchemy(app)
secret_key = os.environ.get('SECRET_KEY')
app.secret_key = secret_key

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def set_password(self, password, salt):
        combined = (password + str(salt)).encode('utf-8')
        self.password_hash = generate_password_hash(sha256(combined).hexdigest(), method='pbkdf2:sha256:120000')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    try:
        dpw_validate_password(request.form.get('password'))
        salt = secrets.token_bytes(16)
        new_user = User(username=request.form.get('username'))
        new_user.set_password(request.form.get('password'), salt)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return "Invalid password", 400
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return "Invalid credentials", 400
    session['user_id'] = user.id
    return redirect(url_for('view_post', post_id=1))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def comment(post_id):
    if 'user_id' not in session:
        return "You must be logged in to comment", 401
    content = request.form.get('content')
    user_id = session['user_id']
    post = Post.query.get(post_id)
    author = User.query.get(user_id)
    if not author or not post:
        return "Invalid request", 400
    new_comment = Comment(content=content, post=post, author=author)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post_id))

if __name__ == '__main__':
    app.run(debug=False if os.environ.get('FLASK_ENV') != 'development' else True)
