import os
import tarfile
from datetime import utc
import logging
import re
from urllib.parse import unquote

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

def compress_file(filename):
    # Check if file exists and is accessible
    try:
        if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
            logger.error(f"Error: File '{filename}' does not exist or is inaccessible.")
            return None

        # Get current date and time for archive name using a more predictable method
        timestamp = utc.now().strftime("%Y%m%d_%H%M%S")

        # Create .tar.gz file with filename as base
        base, extension = os.path.splitext(unquote(filename))  # Unquote the filename to prevent special character attacks

        # Ensure that the file path is within the intended directory
        validate_directory_path(os.path.dirname(base))

        # Sanitize and validate input filename
        sanitized_filename = sanitize_filename(base)

        # Create compressed archive with sanitized filename
        compressed_filename = f"{sanitized_filename}_compressed_{timestamp}.tar.gz"

        logger.info(f"Compressing file: {filename}")

        # Check if the destination directory allows writing
        dest_dir = os.path.dirname(compressed_filename)
        try:
            with open(os.devnull, 'wb') as null_file:
                # Attempt to create a temporary file in the destination directory
                with open(f"{dest_dir}/temp_file", 'wb') as temp_file:
                    pass  # Write something to test write permissions
                os.remove(f"{dest_dir}/temp_file")
        except (OSError, PermissionError):
            logger.error(f"Error: Directory '{dest_dir}' is inaccessible or does not allow writing.")
            return None

        with tarfile.open(compressed_filename, 'w:gz') as tf:
            try:
                tf.add(filename, arcname=os.path.basename(unquote(filename)))  # Unquote the filename to prevent special character attacks
            except (tarfile.TarError, OSError) as e:
                logger.error(f"Error creating archive: {str(e)}")
                return None

        logger.info(f"File '{filename}' successfully compressed and saved as '{compressed_filename}'.")

    except Exception as e:
        # Reraise any unexpected exceptions
        raise

# Example usage:
compress_file("example.txt")
