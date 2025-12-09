import os
from flask import Flask

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    # Add other configurations as needed

def configure_app(app):
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(f'config.{config_name.capitalize()}Config')

if not app.debug:
    # Additional security configurations for non-debug environments
    pass

# Set default configuration
app = Flask(__name__)
configure_app(app)

if __name__ == '__main__':
    app.run()
