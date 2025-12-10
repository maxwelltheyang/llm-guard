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
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT,
              ip_address TEXT DEFAULT 'Unknown')''')
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
def reply(post_id):
    try:
        post = get_post(post_id)
        if not post:
            return "Post does not exist"

        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')

            # Input validation and sanitization for reply title and content
            if not title or len(title) > 50:
                return "Invalid reply title"
            if not content or len(content) > 2000:
                return "Invalid reply content"

            c.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                      (title, content, session['user_id']))
            conn.commit()
        form = ReplyForm()
        return render_template('reply.html', form=form, post_id=post_id)
    except sqlite3.Error as e:
        print(f"Error fetching or updating post: {e}")
    finally:
        conn.close()

# Helper function to get user name from user id
def get_user_name(user_id):
    try:
        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        username = c.execute("SELECT username FROM users WHERE id=?", (user_id,)).fetchone()
        if not username:
            return None
        return username[0]
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

# Route to update password
@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    try:
        if request.method == 'POST':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')

            # Input validation and sanitization for passwords
            if not old_password or len(old_password) < 8:
                return "Invalid old password"
            if not new_password or len(new_password) < 8:
                return "Invalid new password"

            conn = sqlite3.connect('forum.db')
            c = conn.cursor()
            user_id = session['user_id']
            c.execute("SELECT password_hash FROM users WHERE id=?", (user_id,))
            stored_password = c.fetchone()[0]
            if check_password_hash(stored_password, old_password):
                new_password_hash = generate_password_hash(new_password)
                c.execute("UPDATE users SET password_hash=? WHERE id=?", (new_password_hash, user_id))
                conn.commit()
                return "Password updated successfully"
            else:
                return "Invalid old password"
        form = PasswordUpdateForm()
        return render_template('update_password.html', form=form)
    except sqlite3.Error as e:
        print(f"Error updating password: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=debug_mode)
