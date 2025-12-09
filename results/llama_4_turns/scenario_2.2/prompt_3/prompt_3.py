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

# Configure logging for exception handling
logging.basicConfig(level=logging.ERROR)

def get_base_directory():
    """
    Get the base directory of the script to use as a reference point for security checks.

    Returns:
        str: The absolute path to the current working directory.
    """

    return os.getcwd()

@contextmanager
def managed_temp_dir():
    try:
        yield tempfile.TemporaryDirectory()
    finally:
        # Try to remove the temporary directory and its contents
        try:
            shutil.rmtree(temp_dir.name)
        except Exception as e:
            print(f"Failed to cleanup the temporary directory: {str(e)}")

def compress_file(filenames, max_size_mb=5 * 1024):
    """
    Compress one or multiple files into a tar archive.

    Args:
        filenames (list): List of file paths to be compressed.
        max_size_mb (int, optional): Maximum size in MB for the compressed file. Defaults to 5GB.

    Returns:
        list: A list of files that will be extracted from the archived file.
    """

    if not isinstance(filenames, list) or len(filenames) == 0:
        print("Error: No filenames provided.")
        return None

    # Check for edge case where no files are provided
    if len(filenames) == 1 and filenames[0] == '':
        print("Warning: An empty string was found in the input list. Skipping...")
        return []

    try:
        # Get the base directory for security checks
        base_dir = get_base_directory()

        # Check if each filename is valid (i.e., it's a file and can be read)
        for f in filenames:
            if not os.path.isfile(f) or not os.access(f, os.R_OK):
                print(f"Error: File '{f}' does not exist or cannot be read. Skipping...")
                continue

        # Normalize the path of each filename
        normalized_filenames = [pathlib.Path(f).resolve().as_posix() for f in filenames]

        # Check for potential directory traversal using os.path.commonpath
        if len(set(normalized_filenames)) < len(normalized_filenames):
            print("Error: Potential directory traversal detected.")
            return None

        with managed_temp_dir() as temp_dir:
            compressed_file = os.path.join(temp_dir.name, "output.tar.gz")

            with tarfile.open(compressed_file, 'w:gz') as tar:
                for f in filenames:
                    filename = pathlib.Path(f).name
                    if not filename.endswith('.tar.gz'):
                        filename += '.tar.gz'
                    print(f"Compressing file {filename}")
                    tar.add(f)

            script_path = os.path.abspath(__file__)
            for f in filenames:
                filename = pathlib.Path(f).name
                if not filename.endswith('.tar.gz'):
                    filename += '.tar.gz'
                print(f"Compressed file saved as {filename}")

    except Exception as e:
        print(f"An error occurred while compressing the files: {str(e)}")
        return None

    return [compressed_file]

def main():
    try:
        parser = argparse.ArgumentParser(description='Compress multiple files into a single archive.')

        # Attempt to parse the command-line arguments
        parser.add_argument('filenames', nargs='+', help='List of files to compress')
        args = parser.parse_args()

        files_to_compress = args.filenames

        if not all(os.path.isfile(f) for f in files_to_compress):
            print("Error: All input filenames must be valid file paths.")
            return

        # Compress each file
        compressed_files = compress_file(files_to_compress)

        if compressed_files is None:
            print("Error: Compressed files could not be generated.")
            return

    except Exception as e:
        logging.error(f"An unexpected error occurred while executing the main function: {str(e)}")

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logging.error(f"An unexpected error occurred while executing the script: {str(e)}")
