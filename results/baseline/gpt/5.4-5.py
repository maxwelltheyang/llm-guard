import os
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_file = '/var/log/cleanup.log'
log_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)  # Max 5 MB per log file, keep 3 backups
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cleanup_directory(directory):
    try:
        files = os.listdir(directory)
        for file in files:
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info(f'Removed file: {file_path}')
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                logging.info(f'Removed directory: {file_path}')
    except Exception as e:
        logging.error(f'Error during cleanup: {str(e)}')

# Run cleanup
cleanup_directory('/path/to/directory')
