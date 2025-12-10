from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Generate a random secret key for production use

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

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            return "Passwords do not match."

        # Hash the password and insert into database
        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, generate_password_hash(password)))
        conn.commit()
        conn.close()

        return "User registered successfully!"

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve user's password hash from database and check it against the input password
        conn = sqlite3.connect('forum.db')
        c = conn.cursor()
        c.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
        user_data = c.fetchone()

        if user_data is None:
            return "User not found."

        user_id, password_hash = user_data

        # Check if the input password matches the stored hash
        if check_password_hash(password_hash, password):
            session['user_id'] = user_id
            return redirect(url_for('index'))

        return "Incorrect username or password."
    return render_template('login.html')

# Index route (display all posts)
@app.route('/')
def index():
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM posts")
    posts = c.fetchall()

    # Retrieve the user's username for display
    user_id = session.get('user_id')
    if user_id:
        c.execute("SELECT username FROM users WHERE id=?", (user_id,))
        username = c.fetchone()[0]
    else:
        username = None

    conn.close()
    return render_template('index.html', posts=posts, username=username)

# Post route (create a new post)
@app.route('/post', methods=['POST'])
def post():
    title = request.form.get('title')
    content = request.form.get('content')

    # Insert the post into the database
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
              (title, content, session['user_id']))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Reply route (create a new reply)
@app.route('/reply/<int:post_id>', methods=['POST'])
def reply(post_id):
    post_id = int(post_id)
    content = request.form.get('content')

    # Insert the reply into the database
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
              ('Reply to post', content, session['user_id']))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
