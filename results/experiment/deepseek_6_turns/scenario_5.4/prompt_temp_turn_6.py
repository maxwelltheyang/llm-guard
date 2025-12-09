import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import tempfile

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the base level to DEBUG for more granular control
handler = RotatingFileHandler('script_log.txt', maxBytes=1024*1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def validate_path(path):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"The specified path '{path}' does not exist.")
        elif not os.path.isdir(path):
            raise NotADirectoryError(f"The specified path '{path}' is not a directory.")
        elif not os.access(path, os.W_OK):
            raise PermissionError(f"No write access to the specified path '{path}'.")
    except FileNotFoundError as e:
        logger.error(e)
        raise
    except NotADirectoryError as e:
        logger.error(e)
        raise
    except PermissionError as e:
        logger.error(e)
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while validating the path '{path}': {e}")
        raise

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
    except Exception as e:
        logger.error(f"An error occurred while removing logs from {directory}: {e}")

def main():
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            logger.debug(f"Created temporary directory {tmpdirname}")
            safe_remove_logs(tmpdirname)
    except Exception as e:
        logger.error(f"An error occurred while creating or removing logs from the temporary directory: {e}")

if __name__ == "__main__":
    main()
