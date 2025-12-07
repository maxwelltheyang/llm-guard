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

# Configure logging for exception handling and critical events
console = Console()
logging.basicConfig(
    level=logging.INFO,
    handlers=[RichHandler()],
    format="%(message)s"
)

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

def validate_path(dir_path: pathlib.Path) -> None:
    """
    Validate a directory path.

    Args:
        dir_path (pathlib.Path): The path to be validated.

    Raises:
        ValueError: If the directory does not exist or lacks write permissions.
    """

    # Check if the directory exists
    if not dir_path.exists():
        raise ValueError(f"The directory '{dir_path}' does not exist.")

    # Check if the directory has write permissions
    if not dir_path.is_dir() or not dir_path.writeable():
        raise ValueError(f"The directory '{dir_path}' lacks write permissions.")

def compress_file(file_path: pathlib.Path, temp_dir: pathlib.Path) -> None:
    """
    Compress a file into a tarball.

    Args:
        file_path (pathlib.Path): The path to the file being compressed.
        temp_dir (pathlib.Path): The temporary directory where the tarball will be created.

    Raises:
        ValueError: If the file does not exist or lacks read permissions, or if the tarball cannot be written.
    """

    # Validate the file and its parent directory
    validate_path(file_path)
    validate_path(temp_dir / file_path.name)

    try:
        with (temp_dir / f"{file_path.stem}.tar").open('w') as archive:
            with tarfile.open(archive, 'w') as tar:
                tar.add(str(file_path))

        console.log(f"The file '{file_path}' has been successfully archived.")

    except Exception as e:
        logging.error(f"An error occurred while compressing the file: {str(e)}")

def main() -> None:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('filenames', nargs='+', help="One or more filenames to be compressed")
        args = parser.parse_args()

        files_to_compress = args.filenames

        if len(files_to_compress) == 0:
            raise ValueError("At least one filename must be provided")

        # Sanitize the filenames
        sanitized_filenames = []
        for file in files_to_compress:
            try:
                validate_filename(file)
                sanitized_filenames.append(sanitize_filename(file))
            except Exception as e:
                logging.error(f"An error occurred while sanitizing the filename: {str(e)}")

        if len(sanitized_filenames) == 0:
            raise ValueError("All filenames must be provided")

        # Compress each file
        with managed_temp_dir() as temp_dir:
            for file in sanitized_filenames:
                try:
                    compress_file(temp_dir / file, temp_dir)

                except Exception as e:
                    logging.error(f"An error occurred while processing the file: {str(e)}")

        console.log("All files have been successfully archived.")

    except Exception as e:
        logging.error(f"An unexpected error occurred while executing the main function: {str(e)}")

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logging.error(f"An unexpected error occurred while executing the script: {str(e)}")
