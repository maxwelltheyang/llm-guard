from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import secrets
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

app = Flask(__name__)

# Secure environment configuration
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_urlsafe(16))
app.config['SESSION_COOKIE_SECURE'] = True  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

csrf = CSRFProtect(app)

DATABASE = 'database.db'

# Ensure admin credentials are securely set via environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def log_audit(action_description):
    """Log an audit entry."""
    conn = get_db_connection()
    if conn:
        try:
            conn.execute(
                'INSERT INTO audit_log (admin_username, action_description, timestamp) VALUES (?, ?, ?)',
                (ADMIN_USERNAME, action_description, datetime.now())
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging audit entry: {e}")
        finally:
            conn.close()

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash('Failed to connect to the database.', 'error')
        return render_template('index.html', users=[])

    try:
        users = conn.execute('SELECT * FROM users ORDER BY score DESC').fetchall()
    except sqlite3.Error as e:
        flash(f"An error occurred while fetching users: {e}", 'error')
        users = []
    finally:
        conn.close()

    return render_template('index.html', users=users)

@app.route('/update/<int:user_id>', methods=('GET', 'POST'))
def update(user_id):
    if not session.get('logged_in'):
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash('Failed to connect to the database.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_score = request.form['score']

        if not new_score.isdigit() or int(new_score) < 0:
            flash('Invalid score. Please enter a positive number.', 'error')
            conn.close()
            return redirect(url_for('update', user_id=user_id))

        try:
            conn.execute('UPDATE users SET score = ? WHERE id = ?', (new_score, user_id))
            conn.commit()
            flash('Score updated successfully.', 'success')
            log_audit(f"Admin {session.get('username')} updated user ID {user_id} score to {new_score}.")
        except sqlite3.Error as e:
            flash(f"An error occurred while updating the score: {e}", 'error')
        finally:
            conn.close()

        return redirect(url_for('index'))

    try:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    except sqlite3.Error as e:
        flash(f"An error occurred while fetching the user: {e}", 'error')
        user = None
    finally:
        conn.close()

    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('index'))

    return render_template('update.html', user=user)

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE, host='127.0.0.1', port=5000)
