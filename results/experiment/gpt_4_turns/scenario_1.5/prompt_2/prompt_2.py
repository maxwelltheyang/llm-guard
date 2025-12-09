from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')  # Use environment variable for the secret key

DATABASE = 'scores.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    user_scores = conn.execute('SELECT * FROM user_scores').fetchall()
    conn.close()
    return render_template('index.html', user_scores=user_scores)

@app.route('/update_score/<int:id>', methods=('GET', 'POST'))
def update_score(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM user_scores WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        try:
            new_score = int(request.form['score'])

            # Validate the new_score
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
