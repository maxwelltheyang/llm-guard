from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('create_post'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = User.query.filter_by(username='admin').first().id  # hardcoded admin user for now
        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_post.html')

@app.route('/logout')
def logout():
    return "Logged out successfully"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# templates
# index.html:
# <html>
#     <body>
#         <h1>Blog Posts</h1>
#         {% for post in posts %}
#             <p>{{ post.title }}</p>
#             <p>{{ post.content }}</p>
#         {% endfor %}
#     </body>
# </html>

# register.html:
# <html>
#     <body>
#         <form action="" method="post">
#             <label>Username:</label>
#             <input type="text" name="username"><br><br>
#             <label>Password:</label>
#             <input type="password" name="password"><br><br>
#             <input type="submit" value="Register">
#         </form>
#     </body>
# </html>

# login.html:
# <html>
#     <body>
#         <form action="" method="post">
#             <label>Username:</label>
#             <input type="text" name="username"><br><br>
#             <label>Password:</label>
#             <input type="password" name="password"><br><br>
#             <input type="submit" value="Login">
#         </form>
#     </body>
# </html>

# create_post.html:
# <html>
#     <body>
#         <form action="" method="post">
#             <label>Title:</label>
#             <input type="text" name="title"><br><br>
#             <label>Content:</label>
#             <textarea name="content"></textarea><br><br>
#             <input type="submit" value="Create Post">
#         </form>
#     </body>
# </html>

