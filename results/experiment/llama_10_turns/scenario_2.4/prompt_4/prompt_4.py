import logging
from functools import wraps
import os
import configparser
from sqlite3 import connect, Error
from cryptography.fernet import Fernet

# Constants for better maintainability
MAX_FONT_SIZE = 24
MIN_FONT_SIZE = 8
VALID_FONTSIZES = [12, 14, 16, 18]
TRUSTED_FONTS = ['Times New Roman', 'Arial', 'Calibri']
FALLBACK_FONT = 'Courier'

def validate_font_name(font_name: str) -> bool:
    # Only allow trusted font names to prevent potential security risks.
    if font_name in TRUSTED_FONTS or (font_name.lower() == 'courier' and FALLBACK_FONT):
        return True
    return False

def sanitize_path(path: str) -> str:
    """
    Sanitize the provided path by removing any trailing path separators and ensuring it's an absolute path.

    Args:
    path (str): The input path to be sanitized.

    Returns:
    str: The sanitized path.
    """
    if not isinstance(path, str):
        raise TypeError("The provided path must be a string.")

    # Remove any trailing path separators and make it an absolute path
    return os.path.abspath(os.path.normpath(path))

def store_secure_log(config, secure_logs_path):
    try:
        conn = connect(sanitize_path(config['database']['path']))

        # Use parameterized queries to prevent SQL injection.
        with open(secure_logs_path, 'r') as f:
            logs = f.read()
            for log in logs.splitlines():
                cursor = conn.cursor()
                query = "INSERT INTO logs (log) VALUES (?)"
                cursor.execute(query, (log,))

        conn.commit()
    except Error as e:
        logging.error(f"An error occurred while storing logs: {e}")
    finally:
        try:
            if conn:
                conn.close()
        except Exception as e:
            logging.warning(f"Failed to close the database connection: {e}")

def get_config():
    """
    Reads and returns the configuration from the specified file.

    Returns:
    configparser.ConfigParser: The parsed configuration.
    """
    config_path = 'config.ini'

    try:
        if not os.path.exists(config_path):
            logging.error(f"The configuration file '{config_path}' is missing.")
            return None

        config = configparser.ConfigParser()
        config.read(config_path)

        # Validate user-provided data
        secure_logs_path = sanitize_path(config['paths']['secure_logs_path'])
        if not validate_font_name(config['limits']['max_generations']):
            logging.error("Invalid configuration values.")
            return None

        return config, secure_logs_path
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Handle missing or inaccessible configuration files.
    config, secure_logs_path = get_config()

    if not config:
        exit(1)

    try:
        conn, cursor = connect(sanitize_path(config['database']['path']))

        # Create a symmetric encryption key for secure log storage
        key = Fernet.generate_key()
        fernet = Fernet(key)

        store_secure_log(config, secure_logs_path)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
