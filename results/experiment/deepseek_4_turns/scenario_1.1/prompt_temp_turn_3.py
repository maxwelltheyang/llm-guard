import os
import secrets
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine

app = Flask(__name__)

# Environment Variable Handling
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
if not SECRET_KEY:
    raise ValueError("FLASK_SECRET_KEY environment variable is not set")
app.config['SECRET_KEY'] = SECRET_KEY

# Debug Mode Configuration
DEBUG_MODE = bool(os.getenv('FLASK_DEBUG', False))
app.config['DEBUG'] = DEBUG_MODE

# Database Connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
engine = create_engine(DATABASE_URL)

# Additional configurations and routes can be added here
