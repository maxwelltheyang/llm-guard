import logging
from logging.handlers import RotatingFileHandler

# Create a logger
logger = logging.getLogger('my_app')
logger.setLevel(logging.INFO)

# Set up rotating file handler to prevent log files from getting too large
file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024*10, backupCount=5)
file_handler.setLevel(logging.INFO)

# Create a console handler for debug messages
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Set up formatters to format log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Example of secure usage:
try:
    # Attempt to open a file that may not exist
    with open('non_existent_file.txt', 'r') as f:
        data = f.read()
except FileNotFoundError:
    # Log exception securely, avoiding sensitive information disclosure
    logger.exception('Error opening file')
