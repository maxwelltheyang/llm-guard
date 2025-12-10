import os
import tarfile
from datetime import utc
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compress_file(filename):
    # Check if file exists and is accessible
    if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
        logger.error(f"Error: File '{filename}' does not exist or is inaccessible.")
        return None

    try:
        # Get current date and time for archive name using a more predictable method
        timestamp = utc.now().strftime("%Y%m%d_%H%M%S")

        # Create .tar.gz file with filename as base
        base, extension = os.path.splitext(filename)

        # Ensure that the file path is properly escaped to prevent potential attacks (e.g., null byte injection)
        compressed_filename = f"{base}_compressed_{timestamp}.tar.gz"

        logger.info(f"Compressing file: {filename}")

        with tarfile.open(compressed_filename, 'w:gz') as tf:
            # Attempt to add all files in the directory to the tarball
            try:
                tf.add(filename, arcname=filename)
            except tarfile.TarError as e:
                logger.error(f"Error creating archive: {str(e)}")
                return None

        # Check if the compressed file can be written to its destination
        dest_dir = os.path.dirname(compressed_filename)
        try:
            with open(os.devnull, 'wb') as null_file:
                os.symlink(null_file.fileno(), f"{dest_dir}/.test_link")
                os.remove(f"{dest_dir}/.test_link")
        except OSError:
            logger.error(f"Error: Directory '{dest_dir}' is inaccessible or does not allow writing.")
            return None

        logger.info(f"File '{filename}' successfully compressed and saved as '{compressed_filename}'.")

    except PermissionError:
        logger.error("Permission denied. Please ensure you have the necessary permissions to compress this file.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

# Example usage:
compress_file("example.txt")
