from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

# Secret key for secure sessions
app.secret_key = os.urandom(32)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    salt = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.salt = os.urandom(16).hex()
        self.password_hash = generate_password_hash(password + self.salt)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash.replace(user.salt, '', 1), password):
            session['logged_in'] = True
            # Store the logged-in user's ID in session for future use
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_id = session.get('user_id')
        if author_id is not None:
            new_post = Post(title=title, content=content, author_id=int(author_id))
            db.session.add(new_post)
            db.session.commit()
            return 'Posted successfully!'
    return render_template('post.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return 'Logged out'

# Use configuration variables within your Flask app to control debug mode
if 'FLASK_DEBUG' in os.environ and os.environ['FLASK_DEBUG'] == '1':
    app.config['DEBUG'] = True

if __name__ == '__main__':
    app.run()
