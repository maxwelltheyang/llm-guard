import os
from flask import Flask

app = Flask(__name__)

# Use uppercase naming convention for environment variables and set DEBUG based on FLASK_ENV
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))

if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False

# Rest of your application code...
