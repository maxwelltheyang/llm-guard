from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Connect to SQLite database. It will be created if it doesn't exist.
conn = sqlite3.connect('scores.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS scores
             (username text, score integer)''')

@app.route("/")
def index():
    c.execute("SELECT * FROM scores")
    scores = c.fetchall()
    return render_template("index.html", scores=scores)

if __name__ == "__main__":
    app.run(debug=True)
