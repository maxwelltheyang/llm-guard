import os
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
# Generate a random secret key using secrets module for production use
app.secret_key = secrets.token_urlsafe(16)

# Create database and tables if not exist
conn = sqlite3.connect('forum.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, ip_address TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, user_id INTEGER,
              FOREIGN KEY(user_id) REFERENCES users(id))''')
conn.commit()
conn.close()

# Set debug mode using environment variable for production use
debug_mode = os.environ.get('FLASK_DEBUG', 'True') == 'True'
app.config['DEBUG'] = debug_mode

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
    submit = SubmitField('Post')

class ReplyForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content')
    submit = SubmitField('Reply')

# Route to create a new post
@app.route('/post', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        # Input validation and sanitization for post title and content
        if not title or len(title) > 50:
            return "Invalid post title"
        if not content or len(content) > 2000:
            return "Invalid post content"

        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                      (title, content, session['user_id']))
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for('index'))

    return render_template('post.html', form=form)

# Route to create a new reply
@app.route('/reply/<int:post_id>', methods=['GET', 'POST'])
def create_reply(post_id):
    post = get_post(post_id)
    if not post:
        return "Post not found"

    if request.method == 'POST':
        title = form.title.data or 'Reply to post'
        content = form.content.data + "\n\nReplied by user: " + get_user_name(session['user_id'])

        # Input validation and sanitization for reply title and content
        if not title or len(title) > 50:
            return "Invalid reply title"
        if not content or len(content) > 2000:
            return "Invalid reply content"

        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                      (title, content, session['user_id']))
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for('index'))

    form = ReplyForm()
    return render_template('reply.html', form=form, post_id=post_id)

# Helper function to get user name from user id
def get_user_name(user_id):
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    try:
        c.execute("SELECT username FROM users WHERE id=?", (user_id,))
        return c.fetchone()[0]
    except sqlite3.Error as e:
        print(f"Error fetching user name: {e}")
    finally:
        conn.close()

# Helper function to get post from its id
def get_post(post_id):
    try:
        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        post = c.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
        if not post:
            return None
        return post
    except sqlite3.Error as e:
        print(f"Error fetching post: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=debug_mode)
