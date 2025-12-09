import os
from flask import Flask

app = Flask(__name__)

# Use environment variables for configuration settings
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))
