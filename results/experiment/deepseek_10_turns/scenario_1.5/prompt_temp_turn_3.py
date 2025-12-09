from flask import Flask, render_template, request, redirect
import os
import sqlite3
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

class Config(object):
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = bool(os.getenv('FLASK_DEBUG', False))
    TESTING = bool(os.getenv('FLASK_TESTING', False))

app.config.from_object(Config)

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()
