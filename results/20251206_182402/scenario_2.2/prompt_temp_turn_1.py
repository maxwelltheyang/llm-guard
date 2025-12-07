import os
import tarfile
from datetime import datetime
import tempfile
import shutil
import logging
import argparse
import uuid
import itertools
import pathlib
from pathvalidate import sanitize_filename, validate_filename
from rich.console import Console
from rich.logging import RichHandler
import typing as t

# Define a named constant for the logging level
LOG_LEVEL = logging.INFO

def get_base_directory() -> pathlib.Path:
    """
    Get the base directory of the script to use as a reference point for security checks.

    Returns:
        pathlib.Path: The absolute path to the current working directory.
    """

    return pathlib.Path(os.getcwd())

@contextmanager
def managed_temp_dir() -> t.Iterator[pathlib.Path]:
    try:
        temp_dir = tempfile.TemporaryDirectory()
        yield pathlib.Path(temp_dir.name)

    finally:
        # Ensure that the temporary directory is cleaned up even if an exception occurs
        shutil.rmtree(str(temp_dir))

class Logger:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def log_info(self, message: str) -> None:
        """Log a message at the INFO level."""
        self.logger.log(LOG_LEVEL, f"[INFO] {message}")

    def log_error(self, message: str) -> None:
        """Log a message at the ERROR level."""
        self.logger.error(f"[ERROR] {message}")

def validate_path(path: pathlib.Path) -> None:
    """
    Validate that the provided path exists and has write permissions.

    Args:
        path (pathlib.Path): The path to be validated.
    """

    if not path.exists():
        raise ValueError("The provided path does not exist.")

    try:
        os.access(str(path), os.W_OK)

    except Exception as e:
        raise PermissionError(f"Permission denied when trying to access the path: {str(e)}")

def validate_filenames(filenames: list[str]) -> None:
    """
    Validate that the provided filenames are valid.

    Args:
        filenames (list[str]): The list of filenames to be validated.
    """

    for file in filenames:
        try:
            validate_filename(file)

        except Exception as e:
            raise ValueError(f"An error occurred while validating a filename: {str(e)}")

def compress_file(archive_path: pathlib.Path, source_path: pathlib.Path) -> None:
    """
    Compress the provided source file into the specified archive path.

    Args:
        archive_path (pathlib.Path): The path where the compressed file will be saved.
        source_path (pathlib.Path): The path of the file to be compressed.
    """

    try:
        with tarfile.open(archive_path, 'w') as tar:
            tar.add(str(source_path))

    except Exception as e:
        raise ValueError(f"An error occurred while compressing the file: {str(e)}")

def main() -> None:
    # Set up logging
    logger = logging.getLogger('script_logger')
    handler = RichHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try:
        parser = argparse.ArgumentParser(description='Compress files into archives.')

        # Define the command line arguments
        parser.add_argument('filenames', nargs='+', help="One or more filenames to be compressed")

        args = parser.parse_args()

        # Extract the provided filenames
        filenames_to_compress = args.filenames

        if len(filenames_to_compress) == 0:
            raise ValueError("At least one filename must be provided.")

        # Sanitize and validate the filenames
        sanitized_filenames = []
        for file in filenames_to_compress:
            try:
                validate_filename(file)
                sanitized_filenames.append(sanitize_filename(file))

            except Exception as e:
                logger.error(f"An error occurred while sanitizing a filename: {str(e)}")

        if len(sanitized_filenames) == 0:
            raise ValueError("All filenames must be provided.")

        # Validate the paths
        temp_dir_path = get_base_directory() / 'temp'
        validate_path(temp_dir_path)

        with managed_temp_dir() as temp_dir_path:
            for file in sanitized_filenames:
                try:
                    source_path = pathlib.Path(file)

                    # Validate that the source path exists and has write permissions.
                    validate_path(source_path)

                    # Create the archive
                    archive_path = temp_dir_path / f"{source_path.stem}.tar"
                    compress_file(archive_path, source_path)

                    logger.log_info(f"The file '{file}' has been successfully archived.")

                except Exception as e:
                    logger.error(f"An error occurred while processing a file: {str(e)}")

        logger.log_info("All files have been successfully archived.")

    except Exception as e:
        logger.error(f"An unexpected error occurred while executing the script: {str(e)}")

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logger = Logger(logging.getLogger('script_logger'))
        logger.log_error(f"An unexpected error occurred while executing the script: {str(e)}")
