import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import tempfile

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('script_log.txt', maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def validate_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path '{path}' does not exist.")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"The specified path '{path}' is not a directory.")
    if not os.access(path, os.W_OK):
        raise PermissionError(f"No write access to the specified path '{path}'.")

def remove_file(file_path):
    try:
        os.remove(file_path)
        logger.info(f"Successfully removed file: {file_path}")
    except FileNotFoundError:
        logger.warning(f"File not found, cannot remove: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied to remove file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to remove file {file_path}: {e}")

def remove_directory(dir_path):
    try:
        os.rmdir(dir_path)
        logger.info(f"Successfully removed directory: {dir_path}")
    except FileNotFoundError:
        logger.warning(f"Directory not found, cannot remove: {dir_path}")
    except PermissionError:
        logger.error(f"Permission denied to remove directory: {dir_path}")
    except Exception as e:
        logger.error(f"Failed to remove directory {dir_path}: {e}")

def safe_remove_logs(directory):
    try:
        validate_path(directory)
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                remove_file(item_path)
            elif os.path.isdir(item_path):
                remove_directory(item_path)
        logger.info(f"Successfully cleaned up directory: {directory}")
    except FileNotFoundError as e:
        logger.error(f"Directory not found, cannot clean up: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied to access or remove items in the directory: {e}")
    except Exception as e:
        logger.error(f"An error occurred while attempting to clean up the directory {directory}: {e}")

def main():
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            safe_remove_logs(tmpdir)
    except Exception as e:
        logger.error(f"A critical error occurred during temporary directory creation or operation: {e}")
