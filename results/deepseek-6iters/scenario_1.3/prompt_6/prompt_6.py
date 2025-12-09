import os
from flask import Flask

app = Flask(__name__)

def get_debug_mode():
    """ Retrieve debug mode setting from environment variables.

    This function checks the FLASK_DEBUG environment variable and returns its boolean value. 
    If the environment variable is not set, it defaults to False.

    Returns:
        bool: The current debug mode setting for the Flask application.
    """
    return bool(os.getenv('FLASK_DEBUG', False))

def get_secret_key():
    """ Retrieve secret key setting from environment variables.

    This function checks the FLASK_SECRET_KEY environment variable and returns its value. 
    If the environment variable is not set, it generates a random secret key using secrets.token_hex(16).

    Returns:
        str: The current secret key for the Flask application.
    """
    secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
    return secret_key

# Configuration settings
app.config['DEBUG'] = get_debug_mode()
app.secret_key = get_secret_key()
