import os
import tarfile
from datetime import datetime
import tempfile
import shutil
import logging
from pathlib import Path
import argparse
from logging.handlers import RotatingFileHandler
import semgrep

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

        # Validate against unexpected directory traversal or parent directory access
        absolute_source_path = os.path.abspath(str(source_path))
        relative_archive_path = str(archive_path.relative_to(os.getcwd()))
        if (absolute_source_path.startswith(relative_archive_path) and 
            not absolute_source_path.endswith(relative_archive_path)):
            raise ValueError(f"Unexpected directory traversal detected. Archive path '{relative_archive_path}' does not contain the source path '{str(source_path)}'.")

    except Exception as e:
        logger.error(f"An error occurred during archive creation: {str(e)}")

def main() -> None:
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description='Secure Archive Creator')
        parser.add_argument('file', help='Source file path to be archived')
        args = parser.parse_args()

        # Get the source and archive paths
        source_path = Path(args.file)
        archive_name = f"{source_path.stem}.tar"
        temp_dir = tempfile.mkdtemp(prefix="script_temp_")
        archive_path = Path(temp_dir, archive_name)

        # Validate that the source path exists and has write permissions.
        validate_path(source_path)

        # Create the archive
        with tarfile.open(str(archive_path), 'w') as tar:
            tar.add(str(source_path))

        logger.log_info(f"The file '{args.file}' has been successfully archived.")

    except Exception as e:
        # Log security-relevant information and propagate exception downstream.
        raise

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        # Log any errors during execution
        logger.error(f"An unexpected error occurred while executing the script: {str(e)}")
