from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'database.db'
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY score DESC').fetchall()
    conn.close()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)
