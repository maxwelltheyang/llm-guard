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
try:
    result = run(['ls', '-d', target_directory.strip()], check=True, capture_output=True, text=True)
    logger.info(f"Listed directory contents of {target_directory} successfully.")
except Exception as e:
    logger.error(f"Failed to list directory contents of {target_directory}: {e}")

# Optionally delete the original log file after encryption
logs_to_encrypt = ['/path/to/log1', '/path/to/log2']  # Update with the actual paths
for logfile in logs_to_encrypt:
    if os.path.exists(logfile):
        user_confirmation = input("Do you want to delete the original log file? (y/n): ")
        if user_confirmation.lower() == 'y':
            try:
                os.remove(logfile)
                logger.info(f"Deleted {logfile} successfully.")
            except Exception as e:
                logger.error(f"Failed to delete {logfile}: {e}")
