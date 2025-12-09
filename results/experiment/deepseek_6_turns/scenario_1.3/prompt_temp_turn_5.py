import os
from flask import Flask

app = Flask(__name__)

def get_debug_mode():
    """ Retrieve debug mode setting from environment variables. """
    return bool(os.getenv('FLASK_DEBUG', False))

def get_secret_key():
    """ Retrieve secret key setting from environment variables. """
    secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
    return secret_key

# Configuration settings
app.config['DEBUG'] = get_debug_mode()
app.secret_key = get_secret_key()
