import tarfile
import os
import logging
from argparse import ArgumentParser
from datetime import date
import stat
import sys
from pathlib import Path
from typing import List

# Configure basic logging
logging.basicConfig(level=logging.INFO)

class CompressionError(Exception):
    """Base class for exceptions in this module."""
    pass

def compress_file(filenames: List[str], output_filename: str) -> None:
    try:
        for filename in filenames:
            abs_filename = Path(filename).resolve()

            # Validate that file is within current working directory
            if not abs_filename.parent == Path(os.getcwd()):
                raise ValueError("Invalid filename. Filename cannot be outside of current working directory.")

            with tarfile.open(output_filename, "w:gz") as tar:
                tar.add(abs_filename)
            logging.info(f"Compressed {filename} successfully.")
    except FileNotFoundError:
        logging.error(f"Error compressing {filenames}: File not found.", exc_info=True)
    except OSError as e:
        logging.error(f"Error writing to compressed file: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred while compressing files: {str(e)}", exc_info=True)

def get_default_output_filename(filenames: List[str]) -> str:
    try:
        today = date.today()
        base, ext = Path(filenames[0]).name.rsplit('.', 1)
        output_filename = f"{base}_{today.strftime('%Y%m%d')}_compressed.tar.gz"

        # If there are multiple files, append their count to the output filename
        if len(filenames) > 1:
            output_filename += f"_{len(filenames)}"

        return Path(output_filename).as_posix()
    except Exception as e:
        raise ValueError(f"Failed to generate default output filename: {str(e)}")

def check_filename_availability(output_filename: str) -> None:
    existing_file = Path(output_filename)
    if existing_file.exists() and not os.path.samefile(output_filename, existing_file.as_posix()):
        raise ValueError(f"Output filename '{output_filename}' is already in use.")

def validate_output_directory(dir_path: str) -> None:
    try:
        dir_path = Path(dir_path).resolve()
        if not dir_path.exists():
            raise NotADirectoryError(f"Invalid output directory: {dir_path}")

        write_permitted = os.access(dir_path, os.W_OK)

        # Check for potential race conditions by creating a temporary file
        temp_file = dir_path / "temp"
        try:
            with open(temp_file, 'w') as f:
                pass

            # Remove the temporary file to avoid cluttering the directory
            import shutil
            shutil.rmtree(temp_file)

            if not write_permitted:
                raise PermissionError(f"Permission denied for output directory: {dir_path}")
        except Exception as e:
            logging.error(f"An error occurred while checking output directory permissions: {str(e)}")
            raise

    except NotADirectoryError as e:
        logging.error(f"Invalid output directory: {dir_path}. {str(e)}")

def main():
    parser = ArgumentParser(description="Compress files")
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
