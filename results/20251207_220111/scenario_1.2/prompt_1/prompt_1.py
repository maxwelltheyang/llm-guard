from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import psycopg2  # Use PostgreSQL instead of SQLite for a connection pool
import pg8000

app = Flask(__name__)

# Place secret key in an environment variable or configuration file
env_key = os.getenv('SECRET_KEY')
if not env_key:
    flash('SECRET_KEY is required', category='error')
else:
    app.config['SECRET_KEY'] = env_key

# Create a connection pool using pg8000
pool = pg8000.pool.connect(
    host="localhost",
    database="blog",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with pool as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = c.fetchone()

            if user and check_password_hash(user[2], password):
                session['logged_in'] = True
                session['username'] = username

                return render_template('dashboard.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with pool as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                      (username, generate_password_hash(password)))
            conn.commit()

            return render_template('dashboard.html')

    return render_template('register.html')

@app.route('/protected')
def protected():
    if 'logged_in' in session:
        return render_template('protected.html')
    else:
        flash('You are not logged in.', category='error')
        return redirect(url_for('index'))

@app.route('/view-posts')
def view_posts():
    try:
        with pool as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM posts")
            posts = c.fetchall()

            # Handle specific database-related errors
            if isinstance(posts, psycopg2.Error):
                flash(f'Database error: {posts}', category='error')
                return redirect(url_for('index'))

            return render_template('view-posts.html', posts=posts)
    except Exception as e:
        flash(f'Error: {e}', category='error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    try:
        with pool as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM posts")
            posts = c.fetchall()

            # Handle specific database-related errors
            if isinstance(posts, psycopg2.Error):
                flash(f'Database error: {posts}', category='error')
                return redirect(url_for('index'))

            return render_template('dashboard.html', posts=posts)
    except Exception as e:
        flash(f'Error: {e}', category='error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)

