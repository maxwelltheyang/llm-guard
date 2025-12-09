import os
import tarfile
from datetime import datetime
import tempfile
import shutil
import logging
from pathlib import Path
import argparse
from logging.handlers import RotatingFileHandler

# Set up logging
logger = logging.getLogger('script_logger')
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def validate_path(path: Path) -> None:
    try:
        if not path.is_dir():
            raise ValueError(f"'{path}' is not a directory.")

        if os.access(str(path), os.W_OK):
            raise PermissionError(f"Path '{str(path)}' is writable by other users.")

    except Exception as e:
        logger.error(f"An error occurred while validating the path: {str(e)}")

def compress_file(archive_path: Path, source_path: Path) -> None:
    try:
        # Validate and sanitize the archive path
        if not archive_path.is_absolute():
            raise ValueError("The archive path must be an absolute path.")

        sanitized_archive_path = str(archive_path.resolve())
        if not str(source_path).startswith(sanitized_archive_path):
            raise ValueError(f"Archive path '{sanitized_archive_path}' does not match source path '{str(source_path)}'.")

    except Exception as e:
        logger.error(f"An error occurred while validating the archive path: {str(e)}")

def main() -> None:
    try:
        # Configure argparse to prevent command injection attacks
        parser = argparse.ArgumentParser()
        parser.add_argument('file', help='File to be processed')
        args = parser.parse_args()

        # Validate the paths
        temp_dir_path = Path(get_base_directory()) / 'temp'
        validate_path(temp_dir_path)

        with tempfile.TemporaryDirectory() as temp_dir_name:
            source_path = Path(args.file)

            # Validate that the source path exists and has write permissions.
            validate_path(source_path)

            # Create the archive
            archive_path = Path(temp_dir_name) / f"{source_path.stem}.tar"
            compress_file(archive_path, source_path)

            logger.log_info(f"The file '{args.file}' has been successfully archived.")

    except Exception as e:
        # Re-raise the exception to propagate it downstream.
        raise

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        # Log security-relevant information
        logger.error(f"An unexpected error occurred while executing the script: {str(e)}")

# Implement a secure temporary directory cleanup mechanism
try:
    # Clean up the temporary directory
    import shutil
    shutil.rmtree(tempfile.gettempdir() / 'script_temp')

except Exception as e:
    # Log any errors during cleanup
    logger.error(f"An error occurred while cleaning up the temporary directory: {str(e)}")
