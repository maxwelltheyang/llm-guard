import os
import datetime
from pathlib import Path
import logging
import yaml
from functools import lru_cache
from typing import Dict

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
    sanitized_path = Path(log_path).resolve()
    if not sanitized_path.is_absolute():
        return None
    if sanitized_path.parent not in LOG_DIRS:
        return None
    try:
        os.chmod(str(sanitized_path), 0o700) # Strict permission mode for read and write access
        return str(sanitized_path)
    except Exception as e:
        print(f"Error sanitizing log path: {str(e)}")
    return None

def load_config(schema: Dict, config_file: str = 'config.yaml') -> Dict:
    """
    Loads configuration data from a YAML file and validates it against the provided schema.

    Args:
        schema (Dict): The configuration schema to validate against.
        config_file (str): The path to the configuration file. Defaults to 'config.yaml'.

    Returns:
        Dict: The validated configuration data or None if validation fails.
    """
    try:
        with open(config_file, 'r') as stream:
            config = yaml.safe_load(stream)
        return schema.dump(config)  # Using Pydantic's dump method for validation
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
    return None

class CustomLogger(logging.Logger):
    def __init__(self, filename: str):
        super().__init__('custom_logger')
        self.file_handler = logging.FileHandler(filename)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.formatter)
        self.addHandler(self.file_handler)

def rotate_logs(config: Dict):
    try:
        rotation_interval = config['rotation_interval']
        rotation_size = config['rotation_size']
        sanitized_paths = [sanitize_log_path(path) for path in os.listdir(LOG_DIRS[0])]
        if len(sanitized_paths) == 0:
            CustomLogger(LOG_FILE).info('No log files found')
            return
        for path in sanitized_paths:
            try:
                if path is None or not Path(path).exists():
                    continue
                file_size = Path(path).stat().st_size
                current_time = datetime.datetime.now()
                # Check for log rotation based on the defined interval and size
                if (current_time - datetime.timedelta(days=rotation_interval)).timestamp() > datetime.datetime.now().timestamp() or file_size >= rotation_size:
                    os.remove(path)
                    CustomLogger(LOG_FILE).info(f"Removed {path}")
            except Exception as e:
                print(f"Error rotating logs: {str(e)}")
    except Exception as e:
        CustomLogger(LOG_FILE).info(str(e))

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
        rotate_logs(config)
