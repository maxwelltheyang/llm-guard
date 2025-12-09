import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
import secrets
import sqlite3

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))  # Use environment variable for secret key

# Configuration for Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id_, username, password_hash):
        self.id = id_
        self.username = username
        self.password_hash = password_hash

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
    except Exception as e:
        print(f"Error loading user: {e}")
        flash('An unexpected error occurred, please try again later.')
    return None

# Database initialization function
def init_db():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )""")
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        flash('An unexpected error occurred, please try again later.')

# More robust error handling for database operations
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def login():
    try:
        username = request.form['username']
        password = request.form['password']
        user_data = query_db("SELECT * FROM users WHERE username=?", (username,), one=True)
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['password_hash'])
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password')
    except Exception as e:
        print(f"Error during login: {e}")
        flash('An unexpected error occurred, please try again later.')
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return f'Hello, {current_user.username}! This is your profile page.'

if __name__ == '__main__':
    app.run(debug=False)
