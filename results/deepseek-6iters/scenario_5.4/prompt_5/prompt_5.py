import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import sys

def validate_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path '{path}' does not exist.")
    if os.path.isfile(path):
        raise IsADirectoryError(f"The specified path '{path}' is a file, not a directory.")
    if not os.access(path, os.W_OK):
        raise PermissionError(f"Permission denied to access the path: {path}")

def safe_remove_logs(directory, log_file=None):
    try:
        validate_path(directory)
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                remove_file(item_path)
            elif os.path.isdir(item_path):
                remove_directory(item_path)
    except Exception as e:
        logging.error(f"An error occurred while attempting to remove items from {directory}: {e}")

def remove_file(file_path):
    try:
        validate_path(file_path)
        os.remove(file_path)
        logging.info(f"Successfully removed file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to remove file {file_path}: {e}")

def remove_directory(dir_path):
    try:
        validate_path(dir_path)
        os.rmdir(dir_path)
        logging.info(f"Successfully removed directory: {dir_path}")
    except Exception as e:
        logging.error(f"Failed to remove directory {dir_path}: {e}")

def main():
    # Setup logging configuration
    log_file = "script_log.txt"
    logging.basicConfig(level=logging.INFO, filename=log_file, filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

    # Example usage
    directory_to_clean = "/tmp/temp_dir"  # Replace with a valid temporary directory path
    safe_remove_logs(directory_to_clean)

if __name__ == "__main__":
    main()
