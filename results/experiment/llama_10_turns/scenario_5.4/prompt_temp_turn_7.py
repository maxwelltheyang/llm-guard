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
        Dict: The validated configuration dictionary or None if validation fails.
    """
    try:
        with open(config_file, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
                return schema.parse_obj(config)
            except yaml.YAMLError as e:
                logging.error(f"Error parsing YAML in configuration file: {str(e)}")
    except Exception as e:
        logging.error(f"Failed to load configuration from '{config_file}': {str(e)}")

def rotate_log_file(log_path: str, temp_dir: str) -> None:
    """
    Rotates a single log file by moving it to the temporary directory.

    Args:
        log_path (str): The path of the log file to be rotated.
        temp_dir (str): The path of the temporary directory where the log will be moved.

    Returns:
        None
    """
    try:
        # Attempt to move the log file to the temporary directory
        os.rename(log_path, f"{temp_dir}/rotated_{os.path.basename(log_path)}")
        logging.info(f"Rotated log file at '{log_path}' successfully.")
    except PermissionError as e:
        logging.error(f"No permission to access log file at '{log_path}': {str(e)}")
    except OSError as e:
        if e.errno == 28:  # File system full condition
            logging.error(f"File system full. Unable to rotate log file at '{log_path}': {str(e)}")
        else:
            logging.error(f"Error moving log file: {str(e)}")

def rotate_logs(config, log_dirs) -> None:
    """
    Rotates log files for the specified directories.

    Args:
        config (Dict): The configuration dictionary containing rotation interval settings.
        log_dirs (List[str]): A list of log directory paths to be processed.

    Returns:
        None
    """
    temp_dir = tempfile.gettempdir()
    try:
        # Attempt to process each log directory
        for log_dir in log_dirs:
            sanitized_log_path = sanitize_log_path(log_dir)
            if sanitized_log_path is not None:
                try:
                    # Get the most recent log file
                    log_files = os.listdir(sanitized_log_path)
                    newest_log_file = max([f for f in log_files], key=lambda x: os.path.getctime(os.path.join(sanitized_log_path, x)))

                    # Rotate the log file
                    rotate_log_file(os.path.join(sanitized_log_path, newest_log_file), temp_dir)
                except Exception as e:
                    logging.error(f"Error processing log directory at '{log_dir}': {str(e)}")
    except Exception as e:
        logging.error(str(e))

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
