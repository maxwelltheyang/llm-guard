import os
import tarfile
from pathlib import Path
import logging

# Set up a logger for this function
logger = logging.getLogger(__name__)

def compress_file(filename):
    """
    Compress a file into a .tar.gz archive.

    Args:
        filename (str): The name of the file to be compressed.
    """

    # Check if input is a string
    if not isinstance(filename, str):
        raise TypeError("Filename must be a string.")

    # Sanitize the input filename using Path and remove leading/trailing whitespace
    sanitized_filename = Path(filename).resolve().stem

    # Get the absolute path of the file
    filepath = Path(filename).absolute()

    # Check if the file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File '{filename}' not found.")

    # Create a .tar.gz archive with the same name as the input file
    tarball_name, _ = os.path.splitext(sanitized_filename)
    tarball_name += '.tar.gz'

    try:
        # Compress the file into a .tar.gz archive
        with tarfile.open(tarball_name, 'w:gz') as tar:
            tar.add(filepath, arcname=os.path.basename(filepath))
        logger.info(f"File '{filename}' compressed successfully.")
    except PermissionError as e:
        raise Exception(f"Permission denied: {e}")
    except OSError as e:
        raise Exception(f"Failed to compress file: {e}")

# Example usage
if __name__ == "__main__":
    filename = input("Enter the filename: ")
    try:
        compress_file(filename)
    except Exception as e:
        logger.error(f"Error compressing file: {e}")
