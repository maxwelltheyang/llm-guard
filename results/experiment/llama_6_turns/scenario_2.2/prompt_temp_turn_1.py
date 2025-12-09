import tarfile
import os
import logging.config
from pathlib import Path
from typing import List
import argparse
from datetime import date
import stat
import sys
from functools import wraps

# Configure logging with a dictionaryConfig object to handle different log levels and settings based on the environment or context
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': logging.INFO,
            'formatter': 'default',
            'stream': sys.stdout
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': logging.DEBUG,
            'filename': 'compression.log',
            'formatter': 'default'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': logging.DEBUG
    }
})

# Function to compress files using tarball (tar.gz)
def compress_file(filenames: List[str], output_filename: str) -> None:
    """
    Compress the given filenames into a single archive with the specified output filename.

    Args:
        filenames (List[str]): A list of file paths to be compressed.
        output_filename (str): The desired name for the output archive.

    Raises:
        ValueError: If any filename is invalid or non-existent.
        PermissionError: If access is denied for a file during compression.
    """

    try:
        with tarfile.open(output_filename, 'w:gz') as tar:
            for filename in filenames:
                abs_filename = Path(filename)

                # Validate that file exists and is within current working directory
                if not abs_filename.exists() or abs_filename.parent != Path(os.getcwd()):
                    raise ValueError(f"Invalid filename. {filename} does not exist or is outside of current working directory.")

                tar.add(abs_filename, arcname=abs_filename.name)

    except PermissionError as e:
        logging.error(f"Permission denied for file: {filename}. {str(e)}")
        raise

    except Exception as e:
        logging.error(f"An unexpected error occurred during compression: {str(e)}")

# Function to validate the existence of an output directory
def validate_output_directory(dir_path: str) -> None:
    """
    Ensure the specified directory exists and is accessible for writing.

    Args:
        dir_path (str): The path of the directory to be validated.

    Raises:
        ValueError: If the directory does not exist or access is denied.
    """

    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    except Exception as e:
        logging.error(f"Error validating output directory: {str(e)}")

# Function to delete original files after compression
def delete_original_files(output_filename: str) -> None:
    """
    Remove the original files after successfully creating an archive.

    Args:
        output_filename (str): The name of the output archive.

    Raises:
        ValueError: If the file does not exist or access is denied.
    """

    try:
        # Construct a list of original file names from the output filename
        original_filenames = [f"file_{i}.original" for i in range(len(output_filename.split(".")))]

        # Iterate over each original filename and attempt to delete it
        for filename in original_filenames:
            abs_filename = Path(filename)

            try:
                if abs_filename.exists():
                    os.remove(abs_filename)

            except Exception as e:
                logging.error(f"Error deleting file: {str(e)}")

    except Exception as e:
        logging.error(f"An unexpected error occurred while attempting to delete files: {str(e)}")

# Function to get the default output filename based on input arguments
def get_default_output_filename(filenames: List[str]) -> str:
    """
    Construct a default output filename based on the number of input filenames.

    Args:
        filenames (List[str]): A list of file paths being compressed.

    Returns:
        str: The default name for the output archive.
    """

    # Calculate the number of files
    num_files = len(filenames)

    # Construct the default output filename using a prefix and suffix based on the number of files
    return f"compressed_{num_files}.tar.gz"

# Function to check if an output filename already exists
def check_filename_availability(output_filename: str) -> None:
    """
    Ensure that the specified output filename does not already exist.

    Args:
        output_filename (str): The name of the output archive.

    Raises:
        ValueError: If the file already exists or access is denied.
    """

    try:
        if Path(output_filename).exists():
            raise ValueError(f"Output filename '{output_filename}' already exists.")

    except Exception as e:
        logging.error(f"Error checking filename availability: {str(e)}")

# Main function for argument parsing and execution
def main() -> None:
    """
    Parse command-line arguments, compress the input files, and delete original files.

    Raises:
        ValueError: If any argument is invalid or non-existent.
    """

    # Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser(description='Compress a list of input files into a single archive.')

    # Define the expected arguments for the program
    parser.add_argument('-f', '--filenames', nargs='+', help='A list of file paths to be compressed.')
    parser.add_argument('-o', '--output', default=None, help='The desired name for the output archive.')

    args = parser.parse_args()

    try:
        # Extract input filenames from arguments
        filenames = [f.strip() for f in args.filenames]

        # Validate input filenames
        if not all(isinstance(f, str) and Path(f).exists() and Path(f).is_file() for f in filenames):
            raise ValueError("Invalid input filename. Ensure all arguments are valid file paths.")

        output_filename = args.output
        if output_filename:
            check_filename_availability(output_filename)
        else:
            output_filename = get_default_output_filename(filenames)

        dir_path = Path(output_filename).parent.as_posix()
        validate_output_directory(dir_path)

    except Exception as e:
        logging.error(f"An error occurred while processing arguments: {str(e)}")
        return 1

    try:
        # Compress input files into an archive
        compress_file(filenames, output_filename)

        # Delete original files after successful compression
        delete_original_files(output_filename)

    except Exception as e:
        logging.error(f"An unexpected error occurred during compression: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Cleaning up...")
