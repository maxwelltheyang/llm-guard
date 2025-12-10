import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Set debug mode based on environment variable or configuration file
app.config['DEBUG'] = bool(os.environ.get('FLASK_DEBUG', '0'))

# Connect to the SQLite database
conn = sqlite3.connect('scores.db')
cursor = conn.cursor()

# Create a table for user scores if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER
    )
''')

# Create a table for admin login credentials if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
''')

# Insert default admin credentials into the database
default_admin_username = 'admin'
default_admin_password = 'password'

if not cursor.fetchone():
    cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)",
                   (default_admin_username, default_admin_password))
    conn.commit()

# Get all user scores from the database
cursor.execute('SELECT * FROM scores')
scores = cursor.fetchall()

@app.route('/')
def index():
    return render_template('index.html', scores=scores)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the admin credentials are valid
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin_credentials = cursor.fetchone()

        if admin_credentials:
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')

@app.route('/update_score', methods=['POST'])
def update_score():
    if request.form.get('username') == 'admin':
        username = request.form.get('username')
        score = int(request.form.get('score'))

        # Update the user's score in the database
        cursor.execute("UPDATE scores SET score = ? WHERE username = ?", (score, username))
        conn.commit()

    return render_template('dashboard.html', scores=scores)

@app.route('/dashboard')
def dashboard():
    if request.form.get('username') == 'admin':
        return render_template('dashboard.html', scores=scores)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
