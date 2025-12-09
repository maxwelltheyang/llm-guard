import os
from flask import Flask

app = Flask(__name__)

# Load configurations from environment variables or a config file
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
if not app.config['DEBUG']:
    app.config.from_pyfile('production_config.cfg')  # Adjust this to your production configuration loading method
