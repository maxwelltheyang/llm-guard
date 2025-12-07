import os
import logging
from logging.handlers import RotatingFileHandler

# Set up logging configuration
log_file = '/var/log/cleanup.log'
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# Example log message
logger.debug('Logging setup completed.')
