import os
from flask import Flask

app = Flask(__name__)

# Load configurations from environment variables or a config file
app.config.from_object('your_config_module')  # Replace with your actual config module

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
