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

# Define the directories to check for log files with path validation
LOG_DIRS = ["/var/log/apache2", "/var/log/nginx", "/var/log/syslog"]
VALID_LOG_DIRS = set(LOG_DIRS)

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
            config = yaml.safe_load(stream)
            return schema.parse_obj(config)
    except FileNotFoundError as e:
        logging.error(f"Configuration file '{config_file}' not found.")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML in configuration file: {str(e)}")
        raise

def rotate_logs(config, log_dirs):
    """
    Rotates log files based on the provided configuration settings.

    Args:
        config (Dict): The configuration dictionary containing rotation interval and size.
        log_dirs (set): A set of directories to check for log files.
    """
    try:
        if not log_dirs:
            logging.info('No log files found')
            return
        for path in [p for p in log_dirs if Path(p).exists()]:
            file_size = Path(path).stat().st_size
            start_time = time.time()
            # Check for log rotation based on the defined interval and size using a more precise timing mechanism
            if (start_time - config.rotation_interval * 86400) > time.time() or file_size >= config.rotation_size:
                try:
                    shutil.move(path, str(tempfile.gettempdir()))
                    logging.info(f"Moved {path} to temporary directory")
                except Exception as e:
                    logging.error(f"Error moving log file: {str(e)}")
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
        rotate_logs(config, LOG_DIRS)
