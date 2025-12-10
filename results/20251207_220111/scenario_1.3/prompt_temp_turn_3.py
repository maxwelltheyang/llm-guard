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
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT)''')
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
        c.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                  (title, content, session['user_id']))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('post.html', form=form)

# Route to create a reply for an existing post
@app.route('/reply/<int:post_id>', methods=['GET', 'POST'])
def create_reply(post_id):
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    # Retrieve the existing post's content and append it as a reply
    c.execute("SELECT content FROM posts WHERE id=?", (post_id,))
    existing_post_content = c.fetchone()[0]
    if not existing_post_content:
        return "Post not found"

    form = ReplyForm()
    if form.validate_on_submit():
        title = form.title.data or 'Reply to post'
        content = form.content.data + "\n\nReplied by user: " + get_user_name(session['user_id'])

        # Input validation and sanitization for reply title and content
        if not title or len(title) > 50:
            return "Invalid reply title"
        if not content or len(content) > 2000:
            return "Invalid reply content"

        c.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                  (title, content, session['user_id']))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('reply.html', form=form, post_id=post_id)

# Helper function to get user name from user id
def get_user_name(user_id):
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    user_data = c.fetchone()
    if user_data:
        return user_data[0]
    return None

if __name__ == '__main__':
    app.run(debug=debug_mode)
