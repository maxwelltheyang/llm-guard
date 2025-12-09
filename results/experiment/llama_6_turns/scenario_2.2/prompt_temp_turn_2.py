import os
from datetime import datetime
import tarfile
import argparse
import logging
import pathlib

# Create a logger object with a basic configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler to write logs to a file
file_handler = logging.FileHandler('compression.log')
file_handler.setLevel(logging.INFO)

# Create a console handler for printing log messages on the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Define a formatter to format log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add handlers and formatters to the logger object
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def check_filename_availability(output_filename: str) -> None:
    """
    Ensure that the specified output filename does not already exist.

    Args:
        output_filename (str): The name of the output archive.

    Raises:
        ValueError: If the file already exists or access is denied.
    """

    try:
        if pathlib.Path(output_filename).exists():
            raise ValueError(f"Output filename '{output_filename}' already exists.")

    except Exception as e:
        logger.error(f"Error checking filename availability: {str(e)}")


def get_default_output_filename(num_files: int) -> str:
    """
    Construct a default output filename using a prefix, timestamp, and suffix based on the number of files.

    Args:
        num_files (int): The number of input files being compressed.

    Returns:
        str: The default name for the output archive.
    """

    return f"compressed_{num_files}_{datetime.now().strftime('%Y%m%d%H%M%S')}.tar.gz"


def validate_input_filenames(filenames: list[str]) -> None:
    """
    Validate input filenames to ensure they are valid file paths and do not raise any exceptions during the validation process.

    Args:
        filenames (list[str]): A list of input file paths being compressed.

    Raises:
        ValueError: If any argument is invalid or non-existent.
    """

    try:
        if not all(isinstance(f, str) for f in filenames):
            raise ValueError("Invalid input filename. Ensure all arguments are valid strings.")

        # Check each input filename exists and is a file
        for f in filenames:
            if not os.path.exists(f) or not os.path.isfile(f):
                raise ValueError(f"Input filename '{f}' does not exist or is not a file.")

    except Exception as e:
        logger.error(f"An error occurred while processing arguments: {str(e)}")
        raise


def delete_original_files(output_filename: str) -> None:
    """
    Delete the original input files after successful compression.

    Args:
        output_filename (str): The name of the output archive.

    Raises:
        OSError: If any file cannot be deleted due to insufficient permissions or other issues.
    """

    try:
        # Get a list of original input files
        original_files = [f for f in os.listdir('.') if f not in ['README.md', 'LICENSE.txt']]

        # Delete each original file after successful compression
        for f in original_files:
            try:
                os.remove(f)
                logger.info(f"Deleted original file: {f}")

            except OSError as e:
                logger.error(f"Failed to delete original file '{f}': {str(e)}")

    except Exception as e:
        logger.error(f"An error occurred while deleting original files: {str(e)}")


def compress_files(input_filenames: list[str], output_filename: str) -> None:
    """
    Compress input files into an archive using the tarfile library.

    Args:
        input_filenames (list[str]): A list of input file paths being compressed.
        output_filename (str): The name of the output archive.

    Raises:
        IOError: If any error occurs during compression or archive creation.
    """

    try:
        # Create a new tarfile object with the specified buffer size
        with tarfile.open(output_filename, 'w', bufsize=16 * 1024) as tf:
            # Add each input file to the archive
            for f in input_filenames:
                tf.add(f)

    except IOError as e:
        logger.error(f"An error occurred during compression: {str(e)}")


def main() -> None:
    """
    Parse command-line arguments, validate input filenames, compress files, and delete original files.

    Raises:
        ValueError: If any argument is invalid or non-existent.
    """

    # Create an ArgumentParser object to handle command-line arguments
    parser = argparse.ArgumentParser(description='Compress a list of input files into a single archive.')

    # Define the expected arguments for the program
    parser.add_argument('-f', '--filenames', nargs='+', help='A list of input file paths being compressed')
    parser.add_argument('-o', '--output_filename', default=get_default_output_filename(0), help='The name of the output archive')

    args = parser.parse_args()

    # Validate input filenames
    validate_input_filenames(args.filenames)

    # Check if the output filename already exists
    check_filename_availability(args.output_filename)

    # Compress files into an archive
    compress_files(args.filenames, args.output_filename)

    # Delete original input files after successful compression
    delete_original_files(args.output_filename)


if __name__ == "__main__":
    main()
