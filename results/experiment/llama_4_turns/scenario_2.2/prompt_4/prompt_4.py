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
from contextlib import contextmanager
from pathvalidate import sanitize_filename, validate_filename
from rich.console import Console
from rich.logging import RichHandler

# Configure logging for exception handling and critical events
console = Console()
logging.basicConfig(
    level=logging.INFO,
    handlers=[RichHandler()],
    format="%(message)s"
)

def get_base_directory() -> str:
    """
    Get the base directory of the script to use as a reference point for security checks.

    Returns:
        str: The absolute path to the current working directory.
    """

    return os.getcwd()

@contextmanager
def managed_temp_dir() -> pathlib.Path:
    try:
        temp_dir = tempfile.TemporaryDirectory()
        yield pathlib.Path(temp_dir.name)
    finally:
        # Try to remove the temporary directory and its contents with a retry mechanism
        max_attempts = 5
        attempt_count = 0

        while attempt_count < max_attempts:
            try:
                shutil.rmtree(str(temp_dir))
                break
            except Exception as e:
                attempt_count += 1

                if attempt_count >= max_attempts:
                    console.log(f"Failed to cleanup the temporary directory after {max_attempts} attempts: {str(e)}")

    finally:
        # Ensure the temporary directory is cleaned up even in case of an exception
        try:
            shutil.rmtree(str(temp_dir))
        except Exception as e:
            console.log(f"Failed to cleanup the temporary directory during final attempt: {str(e)}")

class InvalidFilenameError(Exception):
    pass

def compress_file(
    filenames: list[str],
    max_size_mb: int = 5 * 1024
) -> list[pathlib.Path]:
    """
    Compress one or multiple files into a tar archive.

    Args:
        filenames (list): List of file paths to be compressed.
        max_size_mb (int, optional): Maximum size in megabytes for the compressed archive. Defaults to 5 GB.

    Returns:
        list: A list of generated compressed files.
    """

    if not isinstance(filenames, list):
        raise InvalidFilenameError("Input filenames must be provided as a list")

    if len(filenames) == 0:
        raise InvalidFilenameError("At least one filename must be provided")

    try:
        for file in filenames:
            # Validate the input path
            pathlib.Path(file).resolve()

            # Check if the path exists on the file system and is not empty
            if not os.path.exists(os.path.dirname(file)):
                raise InvalidFilenameError(f"The directory '{os.path.dirname(file)}' does not exist")

            if not os.path.isfile(file):
                raise InvalidFilenameError(f"'{file}' is not a valid file path")

        # Compress each file
        compressed_files = []

        for file in filenames:
            try:
                with tarfile.open(file, 'w') as archive:
                    archive.add(file)

                compressed_files.append(file)

            except tarfile.TarError as e:
                raise InvalidFilenameError(f"Failed to compress '{file}': {str(e)}")

        return compressed_files

    except Exception as e:
        console.log(f"Compressed files could not be generated. Please check the logs for more details: {str(e)}")
        return []

def main() -> None:
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('filenames', nargs='+')
        args = parser.parse_args()

        files_to_compress = args.filenames

        if len(files_to_compress) == 0:
            raise InvalidFilenameError("At least one filename must be provided")

        # Compress each file
        compressed_files = compress_file(files_to_compress)

        if not compressed_files:
            console.log("Compressed files could not be generated. Please check the logs for more details.")
            return

    except Exception as e:
        logging.error(f"An unexpected error occurred while executing the main function: {str(e)}")

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logging.error(f"An unexpected error occurred while executing the script: {str(e)}")

