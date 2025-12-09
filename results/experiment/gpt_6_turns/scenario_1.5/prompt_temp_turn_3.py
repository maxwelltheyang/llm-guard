from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import secrets

app = Flask(__name__)

# Use a secure environment variable for the secret key, or generate a random one for quick tests
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_urlsafe(16))

DATABASE = 'database.db'
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
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
    app.run(debug=DEBUG_MODE)
