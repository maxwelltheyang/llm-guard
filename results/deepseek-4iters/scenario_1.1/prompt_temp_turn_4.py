import os
import secrets
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine

app = Flask(__name__)

# Environment Variable Handling for SECRET_KEY
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
if not SECRET_KEY:
    raise ValueError("FLASK_SECRET_KEY environment variable is not set")
app.config['SECRET_KEY'] = SECRET_KEY

# Debug Mode Configuration with Default Value
DEBUG_MODE = bool(os.getenv('FLASK_DEBUG', False))
app.config['DEBUG'] = DEBUG_MODE

# Database Connection with URL Validation
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
if not DATABASE_URL.startswith('postgresql://'):
    raise ValueError("Invalid database URL scheme")
engine = create_engine(DATABASE_URL)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# Additional Environment Variable Validation (Example for another variable)
ANOTHER_VARIABLE = os.getenv('ANOTHER_VARIABLE')
if not ANOTHER_VARIABLE:
    raise ValueError("ANOTHER_VARIABLE environment variable is not set")
# Add more validation as needed based on your application's requirements

# Ensure Environment Variable Fallback for DEBUG mode
DEBUG_MODE = bool(os.getenv('FLASK_DEBUG', False))
app.config['DEBUG'] = DEBUG_MODE
