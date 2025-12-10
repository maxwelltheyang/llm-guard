import os
import tarfile
from datetime import utc
import logging
import re
from urllib.parse import unquote
import argparse
import sys
import traceback

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectoryTraversalError(Exception):
    """Raised when a directory traversal attack is detected."""
    pass

def sanitize_filename(filename):
    # Remove null bytes from the filename to prevent injection attacks
    filename = filename.replace('\x00', '')

    # Remove any non-ASCII characters and replace them with an underscore
    filename = re.sub(r'[^\x00-\x7F]+', '_', filename)

    return filename

def validate_directory_path(directory):
    # Check if the directory path is within the intended directory
    base_dir = os.path.dirname(os.getcwd())
    if not (directory.startswith(base_dir) and directory.endswith('/')):
        logger.error(f"Directory traversal detected: {directory}")
        raise DirectoryTraversalError("Invalid directory path")

def validate_file_sizes(file_names, max_size_mb):
    for file_name in file_names:
        try:
            file_size = os.path.getsize(file_name)
            if file_size > max_size_mb * 1024 * 1024:
                logger.error(f"File '{file_name}' is too large to be compressed.")
                return False
        except Exception as e:
            # Log the error and continue to process other files
            logger.error(f"Error checking size of file '{file_name}': {str(e)}")

    return True

def compress_file(file_names):
    if not isinstance(file_names, list) or not all(isinstance(file_name, str) for file_name in file_names):
        raise ValueError("Invalid input type. Expected a list of strings.")

    # Check if files exist and are accessible
    for file_name in file_names:
        try:
            if not os.path.isfile(file_name) or not os.access(file_name, os.R_OK):
                logger.error(f"Error: File '{file_name}' does not exist or is inaccessible.")
                return False
        except Exception as e:
            # Log the error and continue to process other files
            logger.error(f"Error processing file '{file_name}': {str(e)}")

    if not validate_file_sizes(file_names, 1024):  # Default max size limit: 1 GB

    # Get current date and time for archive name using a more predictable method
    timestamp = utc.now().strftime("%Y%m%d_%H%M%S")

    # Create .tar.gz file with filename as base
    sanitized_filenames = [sanitize_filename(os.path.basename(unquote(file_name))) for file_name in file_names]

    # Ensure that the file paths are within the intended directories
    validate_directory_paths([os.path.dirname(file_name) for file_name in file_names])

    # Create compressed archive with sanitized filenames
    archive_filename = f"compressed_{timestamp}.tar.gz"

    logger.info(f"Compressing files: {', '.join(file_names)}")

    try:
        with tarfile.open(archive_filename, 'w:gz') as tf:
            for file_name in file_names:
                base, extension = os.path.splitext(unquote(os.path.basename(file_name)))  # Unquote the filename to prevent special character attacks
                tf.add(file_name, arcname=os.path.basename(base))

        logger.info(f"Files successfully compressed and saved as '{archive_filename}'.")

    except Exception as e:
        # Log the error with a detailed message or stack trace
        exc_info = sys.exc_info()
        logger.error(f"Error creating archive: {str(e)}\n{traceback.format_exc()}")
        return False

    return True

def validate_directory_paths(directories):
    for directory in directories:
        # Check if the directory path is within the intended directory
        base_dir = os.path.dirname(os.getcwd())
        if not (directory.startswith(base_dir) and directory.endswith('/')):
            logger.error(f"Directory traversal detected: {directory}")
            raise DirectoryTraversalError("Invalid directory path")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress files into a tarball.")
    parser.add_argument('filenames', nargs='+', help="Filenames to include in the archive")
    args = parser.parse_args()

    if not compress_file(args.filenames):
        logger.error("Compression failed. Aborting.")
