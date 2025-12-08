import logging
from datetime import timedelta
import os

# Create a logger
logger = logging.getLogger('cleanup_logger')
logger.setLevel(logging.INFO)

# Create a file handler and set the rotation to 1 week
file_handler = logging.handlers.TimedRotatingFileHandler('/var/log/cleanup.log', when='W0', interval=1)
file_handler.setLevel(logging.INFO)

# Create a formatter and attach it to the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

def cleanup():
    # Your cleaning code goes here
    try:
        # Simulating some cleanup actions
        os.remove('/tmp/temp_file.txt')
        logger.info('Removed /tmp/temp_file.txt')
    except Exception as e:
        logger.error(f'Failed to remove /tmp/temp_file.txt: {str(e)}')

if __name__ == '__main__':
    cleanup()
