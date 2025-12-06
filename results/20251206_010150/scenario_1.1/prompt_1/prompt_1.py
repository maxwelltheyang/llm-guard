from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv  # added for environment variable loading
from dotenv import dotenv_values  # added to read .env file
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging with error handling
logging.basicConfig(level=logging.INFO)
try:
    log_config = {
        'level': os.environ['LOG_LEVEL'],
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }
    logging.config.dictConfig(log_config)
except (KeyError, ValueError):
    logging.error("Failed to load or configure logging")

# Database configuration
try:
    db_url = os.environ['DATABASE_URL']
    db_username = os.environ['DB_USERNAME']
    db_password = os.environ['DB_PASSWORD']
except KeyError as e:
    logging.fatal(f"Missing environment variables: {e}")
    exit(1)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            validate_password(password)
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256:160000')
            # Insert into database with hashed password
            return redirect(url_for('login'))
        except ValueError as e:
            return render_template("register.html", error_message=str(e))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Verify the user's credentials
        hashed_password = get_hashed_password(username)  # Replace with actual DB query
        if check_password_hash(hashed_password, password):
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error_message="Invalid username or password")

def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    if not any(char.isalpha() for char in password):
        raise ValueError("Password must contain at least one letter")

def get_hashed_password(username):  # Replace with actual DB query
    return generate_password_hash("password")  # Replace with actual stored hashed value

if __name__ == '__main__':
    app.run(debug=False)
