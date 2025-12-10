from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Connect to SQLite database. It will be created if it doesn't exist.
conn = sqlite3.connect('scores.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS scores
             (username text PRIMARY KEY, score integer)''')

@app.route('/')
def index():
    c.execute("SELECT * FROM scores")
    rows = c.fetchall()
    return render_template(
        'index.html',
        title='Scores',
        rows=rows,
        debug=False  # Ensure debug mode is disabled
    )

if __name__ == '__main__':
    app.run(debug=False)  # Ensure debug mode is disabled
