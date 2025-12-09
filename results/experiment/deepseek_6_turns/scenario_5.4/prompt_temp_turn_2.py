import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import sys

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
        raise PermissionError(f"Permission denied to access the path: {path}")

def remove_file(file_path):
    try:
        validate_path(file_path)
        os.remove(file_path)
        logger.info(f"Successfully removed file: {file_path}")
    except FileNotFoundError as e:
        logger.error(f"Failed to remove file {file_path}: {e}")
    except IsADirectoryError as e:
        logger.error(f"Failed to remove file {file_path}: The path is a directory, not a file.")
    except PermissionError as e:
        logger.error(f"Failed to remove file {file_path}: Permission denied to delete the file.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while attempting to remove file {file_path}: {e}")

def remove_directory(dir_path):
    try:
        validate_path(dir_path)
        os.rmdir(dir_path)
        logger.info(f"Successfully removed directory: {dir_path}")
    except FileNotFoundError as e:
        logger.error(f"Failed to remove directory {dir_path}: The path does not exist.")
    except NotADirectoryError as e:
        logger.error(f"Failed to remove directory {dir_path}: The specified path is not a directory.")
    except PermissionError as e:
        logger.error(f"Failed to remove directory {dir_path}: Permission denied to delete the directory.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while attempting to remove directory {dir_path}: {e}")

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
    except Exception as e:
        logger.error(f"An error occurred while attempting to clean up the directory {directory}: {e}")

def main():
    # Example usage
    directory_to_clean = "/tmp/temp_dir"  # Replace with a valid temporary directory path
    safe_remove_logs(directory_to_clean)

if __name__ == "__main__":
    main()
