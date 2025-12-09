import os
from flask import Flask, request, jsonify
import jwt
from functools import wraps
from cryptography.fernet import Fernet
import sqlite3

app = Flask(__name__)

# Use environment variables for SECRET_KEY with validation and default value
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in the environment variables.")

# Validate that the SECRET_KEY is strong enough
def validate_secret_key(secret_key):
    if len(secret_key) < 32:  # Common minimum length for secure keys
        raise ValueError("SECRET_KEY must be at least 32 characters long.")
    return secret_key.encode()

# Use a key management service or hardware security module (HSM) to securely manage the SECRET_KEY.
app.config['SECRET_KEY'] = validate_secret_key(SECRET_KEY)

# Set debug mode based on environment variable, default to False and add a check for SECRET_KEY configuration
if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY must be set in the environment variables.")
app.config['DEBUG'] = bool(os.getenv('FLASK_ENV', 'False'))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = list(filter(lambda x: x["username"] == data["sub"], authorized_users))

            if not current_user:
                return jsonify({'message': 'Token is invalid'}), 403
        except Exception as e:
            print(e)
            return jsonify({'message': 'Token is invalid'}), 403

        return f(*args, **kwargs)
    return decorated

# Initialize SQLite database and create table for books if it doesn't exist
def init_db():
    db_name = os.getenv('DB_NAME', 'books.db')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, author TEXT)''')
    conn.commit()
    conn.close()

# Call init_db when the app starts
if __name__ == '__main__':
    init_db()
