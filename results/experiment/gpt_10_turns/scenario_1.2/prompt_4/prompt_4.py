from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Load secret key from environment variable for improved security
secret_key = os.environ.get('FLASK_SECRET_KEY')
if not secret_key:
    raise ValueError("No FLASK_SECRET_KEY set for the application")
app.secret_key = secret_key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set Flask session configurations to enhance security
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
)

# Initialize database
db = SQLAlchemy(app)

# Initiate rate limiter
limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr
)

# Models for Users and Posts
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    comments = db.Column(db.PickleType, nullable=False, default=[])

# Setup the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        filtered_posts = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) | (Post.content.ilike(f'%{query}%'))
        ).all()
    else:
        filtered_posts = Post.query.all()

    return render_template('index.html', posts=filtered_posts, query=query)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Title and content are required!')
            return redirect(url_for('create'))

        new_post = Post(
            title=title,
            content=content,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            comments=[]
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!')
        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        if 'username' not in session:
            flash('You need to be logged in to comment!')
            return redirect(url_for('login'))

        comment_content = request.form.get('comment')
        if comment_content:
            post.comments.append({
                'username': session['username'],
                'content': comment_content,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            db.session.commit()
            flash('Comment added successfully!')
            return redirect(url_for('post', post_id=post.id))
        else:
            flash('Comment cannot be empty!')

    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            session['username'] = username
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists!')
        else:
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please log in.')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure the debug mode is configurable via an environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode)
