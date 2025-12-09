from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

# Assume we have a SQLite database named 'scores.db', with a table 'user_scores'
# and columns 'id', 'username', and 'score'.

DATABASE = 'scores.db'

def get_db_connection():
    # Establish a connection to the SQLite3 database
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # Retrieve all data from the user_scores table
    user_scores = conn.execute('SELECT * FROM user_scores').fetchall()
    conn.close()
    # Render the data onto an HTML template
    return render_template('index.html', user_scores=user_scores)

if __name__ == '__main__':
    # Determine if debug mode should be activated based on environment variables
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
