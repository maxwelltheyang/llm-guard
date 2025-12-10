from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Brypt(app)  
jwt = JWTManager(app)

# Load environment variables securely from a .env file using python-dotenv library
try:
    load_dotenv()
except Exception as e:
    app.logger.error(f"Failed to load environment variables: {str(e)}")
    return jsonify({'error': 'Failed to load environment variables'}), 500

# Get database credentials from environment variables, handling potential exceptions
DB_HOST = os.getenv('DB_HOST')
if DB_HOST is None or DB_HOST == '':
    raise ValueError("Database host must be provided")

DB_PORT = int(os.getenv('DB_PORT'))
if DB_PORT <= 0:
    raise ValueError("Database port must be a positive integer")

DB_USER = os.getenv('DB_USER')
if DB_USER is None or DB_USER == '':
    raise ValueError("Database user must be provided")

# Store database credentials securely without exposing its decoded value
try:
    DB_PASSWORD = os.getenv('DB_PASSWORD')
except Exception as e:
    app.logger.error(f"Error retrieving database password: {str(e)}")
else:
    db_uri = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/database'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.init_app(app)

# Introduce a retry mechanism with exponential backoff to handle potential database connection failures
import time

def get_db_connection():
    max_retries = 5
    delay = 1
    retries = 0
    while retries < max_retries:
        try:
            db_uri = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/database'
            return SQLAlchemy(app).engine.connect(db_uri=db_uri)
        except Exception as e:
            app.logger.error(f"Database connection failed: {str(e)}")
            retries += 1
            time.sleep(delay * (2 ** retries))
    return None

# Create a function to store hashed passwords securely without exposing the decoded value
def store_hashed_password(password):
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        app.logger.info(f"Hashed password stored successfully: {hashed_password}")
        return hashed_password
    except Exception as e:
        app.logger.error(f"Error storing hashed password: {str(e)}")
        return None

# Rest of the code remains the same...
