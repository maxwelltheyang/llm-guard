from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

DATABASE = 'scores.db'

# Retrieve admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', generate_password_hash('password'))

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_scores = conn.execute('SELECT * FROM user_scores').fetchall()
    conn.close()
    return render_template('index.html', user_scores=user_scores)

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            flash('You were successfully logged in.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were successfully logged out.')
    return redirect(url_for('login'))

@app.route('/update_score/<int:id>', methods=('GET', 'POST'))
def update_score(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM user_scores WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        try:
            new_score = int(request.form['score'])

            if new_score < 0 or new_score > 100:
                flash('Error: Score must be between 0 and 100.')
            else:
                conn.execute('UPDATE user_scores SET score = ? WHERE id = ?', (new_score, id))
                conn.commit()
                flash('Score successfully updated.')
                conn.close()
                return redirect(url_for('index'))
        except ValueError:
            flash('Error: Invalid input. Score must be a number.')

    conn.close()
    return render_template('update_score.html', user=user)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
