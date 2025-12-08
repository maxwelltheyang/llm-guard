import os
import flask
from flask_sqlalchemy import SQLAlchemy

# Create a new Flask application
app = flask.Flask(__name__)

# Configure database settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SECRET_KEY'] = 'secret_key_here'  # Replace with a secure secret key

# Initialize the database
db = SQLAlchemy(app)

# Create a table for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Create a table for posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create a table for comments
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Define routes for user registration and login
@app.route('/register', methods=['POST'])
def register():
    username = flask.request.form['username']
    password = flask.request.form['password']
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return 'User created successfully!'

@app.route('/login', methods=['POST'])
def login():
    username = flask.request.form['username']
    password = flask.request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return 'Logged in successfully!'
    else:
        return 'Invalid credentials!'

# Define routes for posting and commenting
@app.route('/post', methods=['POST'])
def post():
    title = flask.request.form['title']
    content = flask.request.form['content']
    new_post = Post(title=title, content=content)
    db.session.add(new_post)
    db.session.commit()
    return 'Post created successfully!'

@app.route('/comment', methods=['POST'])
def comment():
    post_id = flask.request.form['post_id']
    content = flask.request.form['content']
    new_comment = Comment(content=content, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return 'Comment created successfully!'

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
