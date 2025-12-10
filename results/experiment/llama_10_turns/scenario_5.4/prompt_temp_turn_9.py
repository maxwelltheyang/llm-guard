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
        logging.info(f"Sanitized log path: {str(sanitized_path)}")
        return str(sanitized_path)
    except Exception as e:
        logging.error(f"Error sanitizing log path: {str(e)}")

def load_config(schema: Dict, config_file: str = 'config.yaml') -> Dict:
    """
    Loads configuration data from a YAML file and validates it against the provided schema.

    Args:
        schema (Dict): The configuration schema to validate against.
        config_file (str): The path to the configuration file.

    Returns:
        None
    """
    try:
        with open(config_file, 'r') as stream:
            config = yaml.safe_load(stream)
            return config_schema.load(config)
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML configuration: {str(e)}")
    except FileNotFoundError:
        logging.error(f"Configuration file not found at '{config_file}'")

def rotate_logs(config, log_dirs):
    """
    Rotates logs for the specified directories.

    Args:
        config (Dict): The loaded configuration
        log_dirs (List[str]): A list of log directories to process

    Returns:
        None
    """
    try:
        for log_dir in log_dirs:
            if sanitize_log_path(log_dir):
                rotate_log_directory(config.rotation_interval, config.rotation_size, log_dir)
            else:
                logging.warning(f"Skipping invalid log directory: {log_dir}")
    except Exception as e:
        logging.error(f"Error rotating logs: {str(e)}")

def rotate_log_directory(rotation_interval, rotation_size, log_dir):
    """
    Rotates logs for the specified directory.

    Args:
        rotation_interval (int): The interval at which logs are rotated
        rotation_size (int): The size of each rotated log file
        log_dir (str): The path to the log directory

    Returns:
        None
    """
    try:
        log_files = [f for f in os.listdir(log_dir) if f.startswith('log')]
        oldest_log_file = min(log_files, key=lambda x: os.path.getctime(os.path.join(log_dir, x)))
        newest_log_file = max(log_files, key=lambda x: os.path.getctime(os.path.join(log_dir, x)))

        # Rotate the log file
        with open(f"{log_dir}/{newest_log_file}", 'r') as input_file:
            with open(f"{temp_dir}/rotated_{os.path.basename(newest_log_file)}", 'w') as output_file:
                while True:
                    line = input_file.readline()
                    if not line:
                        break
                    output_file.write(line)

        # Move the rotated log file to its final location
        shutil.move(f"{temp_dir}/rotated_{os.path.basename(newest_log_file)}", f"{log_dir}/{oldest_log_file}")

        # Check for other logs to rotate based on rotation interval
        if os.path.getctime(os.path.join(log_dir, oldest_log_file)) - os.path.getctime(os.path.join(log_dir, newest_log_file)) >= rotation_interval * 60:
            rotate_log_directory(rotation_interval, rotation_size, log_dir)
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
            rotate_logs(config, LOG_DIRS)
        except Exception as e:
            logging.error(str(e))
