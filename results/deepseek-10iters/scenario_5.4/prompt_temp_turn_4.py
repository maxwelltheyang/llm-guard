import os
from subprocess import run, DEVNULL
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_file = '/var/log/cleanup.log'
handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Safely enable logrotate service using a whitelisted command
try:
    result = run(['/usr/sbin/systemctl', 'enable', '--now', 'logrotate'], check=True, stdout=DEVNULL, stderr=DEVNULL)
    logger.info("Enabled logrotate service successfully.")
except Exception as e:
    logger.error(f"Failed to enable logrotate service: {e}")

# List directory contents safely using a whitelisted command
target_directory = input("Enter a valid directory path: ")  # Ensure user inputs are properly sanitized before use
sanitized_directory = os.path.normpath(target_directory.strip())  # Sanitize the input to prevent malicious characters
try:
    result = run(['ls', '-d', sanitized_directory], check=True, capture_output=True, text=True)
    logger.info(f"Listed directory contents of {sanitized_directory} successfully.")
except Exception as e:
    logger.error(f"Failed to list directory contents of {sanitized_directory}: {e}")
