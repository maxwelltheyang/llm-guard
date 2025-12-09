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

# Define a custom exception class for specific error cases
class CompressionError(Exception):
    """Base class for exceptions in this module."""
    pass

def log_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            raise
    return wrapper

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
@log_exceptions
def compress_file(filenames: List[str], output_filename: str) -> None:
    try:
        for filename in filenames:
            abs_filename = Path(filename).resolve()

            # Validate that file is within current working directory
            if not abs_filename.parent == Path(os.getcwd()):
                raise ValueError("Invalid filename. Filename cannot be outside of current working directory.")

            with tarfile.open(output_filename, 'w:gz') as tar:
                tar.add(abs_filename)

    except PermissionError as e:
        logging.error(f"Permission denied for file: {filename}. {str(e)}")
        raise

    except Exception as e:
        logging.error(f"An error occurred while compressing files: {str(e)}")
        raise

# Function to validate output directory permissions
@log_exceptions
def validate_output_directory(dir_path: str) -> None:
    try:
        if not os.path.exists(dir_path):
            raise NotADirectoryError("Output directory does not exist.")

        if not os.access(dir_path, os.W_OK):
            raise PermissionError("Permission denied for output directory.")

    except Exception as e:
        logging.error(f"An error occurred while validating output directory: {str(e)}")
        raise

# Main function
def main():
    parser = argparse.ArgumentParser(description="Compress files")
    parser.add_argument("-f", "--files", nargs="+", help="Filenames to compress (comma-separated string)")
    parser.add_argument("-o", "--output", help="Custom output filename")

    args = parser.parse_args()

    try:
        filenames = [f.strip() for f in args.files]

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
        compress_file(filenames, output_filename)

    except Exception as e:
        logging.error(f"An unexpected error occurred during compression: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Cleaning up...")
