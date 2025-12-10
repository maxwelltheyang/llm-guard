import os
import sqlite3
from flask import Flask, render_template, request

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

# Get all user scores from the database
cursor.execute('SELECT * FROM scores')
scores = cursor.fetchall()

@app.route('/')
def index():
    return render_template('index.html', scores=scores)

@app.route('/update_score', methods=['POST'])
def update_score():
    username = request.form['username']
    score = int(request.form['score'])

    # Update the user's score in the database, using parameterized queries to prevent SQL injection
    cursor.execute('UPDATE scores SET score = ? WHERE username = ?', (score, username))
    conn.commit()

    return 'Score updated successfully!'

if __name__ == '__main__':
    app.run()
