import os
from flask import Flask

app = Flask(__name__)

# Configure logging and other settings
# ... (rest of the configuration)

# Use environment variables to set different configurations based on FLASK_ENV
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
if app.config['FLASK_ENV'] == 'production':
    app.debug = False
