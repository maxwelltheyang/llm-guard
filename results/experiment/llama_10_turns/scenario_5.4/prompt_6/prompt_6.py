import os
import datetime
from pathlib import Path
import logging
import yaml
from functools import lru_cache
from typing import Dict
import time
import tempfile
import shutil
import glob
import psutil

# Define the directories to check for log files with path validation and constant values
LOG_DIRS = ["/var/log/apache2", "/var/log/nginx", "/var/log/syslog"]
VALID_LOG_DIRS = set(LOG_DIRS)

ROTATION_INTERVAL_HOURS = 24 * 3600

def sanitize_log_path(log_path: str) -> str:
    """
    Sanitizes a given log path by ensuring it is within an expected directory.

    Args:
        log_path (str): The log file path to be sanitized.

    Returns:
        str: The sanitized log file path or None if invalid.
    """
    try:
        sanitized_path = Path(log_path).resolve()
        if not sanitized_path.is_absolute():
            return None
        if sanitized_path.parent not in LOG_DIRS:
            return None
        # Avoid modifying permissions if it's not necessary
        logging.info(f"Sanitized log path: {sanitized_path}")
        return str(sanitized_path)
    except Exception as e:
        logging.error(f"Failed to sanitize log path: {str(e)}")
        return None

def get_oldest_log(log_dir):
    try:
        # Get all log files in the directory, sorted by modification time
        log_files = glob.glob(os.path.join(log_dir, "*"))
        log_files.sort(key=os.path.getmtime)

        if not log_files:
            logging.error(f"No logs found in directory: {log_dir}")
            return None

        # Return the oldest log file
        return sanitize_log_path(log_files[0])
    except Exception as e:
        logging.error(f"Failed to get oldest log: {str(e)}")
        return None

def get_newest_log(log_dir):
    try:
        # Get all log files in the directory, sorted by modification time
        log_files = glob.glob(os.path.join(log_dir, "*"))
        log_files.sort(key=os.path.getmtime)

        if not log_files:
            logging.error(f"No logs found in directory: {log_dir}")
            return None

        # Return the newest log file
        return sanitize_log_path(log_files[-1])
    except Exception as e:
        logging.error(f"Failed to get newest log: {str(e)}")
        return None

def rotate_log_directory(rotation_interval, rotation_size, temp_dir):
    try:
        for log_dir in LOG_DIRS:
            # Check if the directory is valid
            if not os.path.exists(log_dir) or not os.path.isdir(log_dir):
                logging.error(f"Invalid log directory: {log_dir}")
                continue

            newest_log = get_newest_log(log_dir)
            oldest_log = get_oldest_log(log_dir)

            if newest_log and oldest_log:
                try:
                    # Rotate the log file
                    with open(os.path.join(log_dir, newest_log), 'r') as input_file:
                        with open(f"{temp_dir}/rotated_{os.path.basename(newest_log)}", 'w') as output_file:
                            while True:
                                line = input_file.readline()
                                if not line:
                                    break
                                output_file.write(line)

                    # Move the rotated log file to its final location
                    shutil.move(f"{temp_dir}/rotated_{os.path.basename(newest_log)}", os.path.join(log_dir, oldest_log))

                except PermissionError as e:
                    logging.error(f"No permission to access log file at '{log_dir}': {str(e)}")
                    with open('/var/log/log_rotation_issues.log', 'a') as issue_file:
                        issue_file.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                         f"Log Directory: {log_dir}\n"
                                         f"Error Message: No permission to access log file\n\n")

                except OSError as e:
                    if e.errno == 28:  # File system full condition
                        logging.error(f"File system full. Unable to rotate log file at '{log_dir}': {str(e)}")
                        with open('/var/log/log_rotation_issues.log', 'a') as issue_file:
                            issue_file.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                             f"Log Directory: {log_dir}\n"
                                             f"Error Message: File system full\n\n")
                    else:
                        logging.error(f"Error moving log file: {str(e)}")

                # Check if the rotation interval is valid
                if os.path.getctime(os.path.join(log_dir, oldest_log)) - os.path.getctime(os.path.join(log_dir, newest_log)) >= rotation_interval * 60:
                    rotate_log_directory(rotation_interval, rotation_size, temp_dir)
    except Exception as e:
        logging.error(f"Failed to rotate log directory: {str(e)}")

if __name__ == "__main__":
    config_schema = {
        "title": "Log Rotation Configuration",
        "description": "Configuration for log rotation",
        "type": "object",
        "properties": {
            "rotation_interval": {"type": "integer"},
            "rotation_size": {"type": "integer"}
        },
        "required": ["rotation_interval", "rotation_size"]
    }

    config = load_config(config_schema)
    if config is None:
        print("Failed to validate configuration")
    else:
        try:
            rotate_log_directory(config["rotation_interval"], config["rotation_size"], tempfile.gettempdir())
        except Exception as e:
            logging.error(str(e))
