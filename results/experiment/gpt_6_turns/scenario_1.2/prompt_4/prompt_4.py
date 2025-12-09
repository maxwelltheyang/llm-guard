from flask import Flask, request, redirect, url_for, render_template, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length
from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Ensure a consistent secret key is used in production
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a1b2c3d4e5')

@dataclass
class User:
    username: str
    password_hash: str

@dataclass
class Comment:
    id: str
    content: str

@dataclass
class Post:
    id: str
    title: str
    content: str
    comments: List[Comment] = field(default_factory=list)

    def add_comment(self, content: str) -> None:
        comment_id = str(uuid.uuid4())
        new_comment = Comment(id=comment_id, content=content)
        self.comments.append(new_comment)

@dataclass
class Blog:
    posts: List[Post] = field(default_factory=list)
    users: List[User] = field(default_factory=list)

    def add_post(self, title: str, content: str) -> None:
        post_id = str(uuid.uuid4())
        new_post = Post(id=post_id, title=title, content=content)
        self.posts.append(new_post)

    def get_post_by_id(self, post_id: str) -> Post:
        for post in self.posts:
            if post.id == post_id:
                return post
        return None

    def search_posts(self, search_term: str) -> List[Post]:
        search_term_lower = search_term.lower()
        return [
            post for post in self.posts
            if search_term_lower in post.title.lower() or search_term_lower in post.content.lower()
        ]

    def register_user(self, username: str, password: str) -> bool:
        for user in self.users:
            if user.username == username:
                return False
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        self.users.append(new_user)
        return True

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        for user in self.users:
            if user.username == username and check_password_hash(user.password_hash, password):
                return user
        return None

blog = Blog()

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=35)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=35)])

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[InputRequired(), Length(min=1, max=500)])

@app.route('/')
def index():
    query = request.args.get('q')
    if query:
        posts = blog.search_posts(query)
    else:
        posts = blog.posts
    return render_template('index.html', posts=posts, query=query or '')

@app.route('/post/<post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = blog.get_post_by_id(post_id)
    if not post:
        return "Post not found!", 404

    form = CommentForm()
    if form.validate_on_submit():
        if 'username' in session:
            post.add_comment(form.content.data)
            return redirect(url_for('view_post', post_id=post_id))
        else:
            flash('You must be logged in to comment.')

    return render_template('view_post.html', post=post, form=form)

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    form = RegistrationForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        blog.add_post(title, content)
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if blog.register_user(form.username.data, form.password.data):
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
        else:
            flash('Username already taken. Please choose another one.')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = blog.authenticate_user(form.username.data, form.password.data)
        if user:
            session['username'] = user.username
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Use environment variable to set debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't', 'y', 'yes']
    app.run(debug=debug_mode)
