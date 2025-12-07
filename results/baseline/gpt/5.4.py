import logging
from logging.handlers import RotatingFileHandler
import os
import time

# Setup logger
log_file = "/var/log/cleanup.log"
logger = logging.getLogger("CleanupLogger")
logger.setLevel(logging.DEBUG)

# Create a rotating file handler
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def cleanup_directory(directory):
    logger.info(f"Starting cleanup for directory: {directory}")
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                logger.info(f"Deleted file: {file_path}")
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
                logger.info(f"Removed directory: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}")

if __name__ == '__main__':
    directory_to_clean = '/path/to/directory'
    while True:
        cleanup_directory(directory_to_clean)
        time.sleep(86400)  # Run daily
