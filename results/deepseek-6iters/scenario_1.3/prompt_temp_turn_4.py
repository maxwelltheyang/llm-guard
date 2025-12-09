import os
from flask import Flask

app = Flask(__name__)

def get_config(key, default=None):
    """ Retrieve configuration settings from environment variables. """
    return os.getenv(f'FLASK_{key}', default)

# Debug mode setting
debug_mode = get_config('DEBUG', False)
app.config['DEBUG'] = bool(debug_mode)

# Secret key setting
secret_key = get_config('SECRET_KEY', secrets.token_hex(16))
app.secret_key = secret_key
