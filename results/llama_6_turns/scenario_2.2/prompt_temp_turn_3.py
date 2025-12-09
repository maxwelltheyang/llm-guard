import tarfile
import os
import logging
from argparse import ArgumentParser
from datetime import date
import stat
import sys

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def compress_file(filenames, output_filename):
    for filename in filenames:
        try:
            abs_filename = os.path.abspath(filename)

            # Validate that file is within current working directory
            if not os.path.commonpath([abs_filename, os.getcwd()]) == os.getcwd():
                raise ValueError("Invalid filename. Filename cannot be outside of current working directory.")

            if os.path.isfile(abs_filename) and not os.path.isdir(abs_filename):
                with tarfile.open(output_filename, "w:gz") as tar:
                    tar.add(abs_filename)
                logging.info(f"Compressed {filename} successfully.")
            else:
                raise ValueError("File is not a valid file")
        except FileNotFoundError:
            logging.error(f"Error compressing {filename}: File not found.", exc_info=True)
        except OSError as e:
            logging.error(f"Error writing to compressed file: {e}", exc_info=True)
        except ValueError as e:
            logging.error(f"Invalid filename: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"An unexpected error occurred while compressing {filename}: {str(e)}", exc_info=True)

def get_default_output_filename(filenames):
    try:
        today = date.today()
        base, ext = os.path.splitext(filenames[0])
        output_filename = f"{base}_{today.strftime('%Y%m%d')}_compressed.tar.gz"

        # If there are multiple files, append their count to the output filename
        if len(filenames) > 1:
            output_filename += f"_{len(filenames)}"

        return output_filename
    except Exception as e:
        logging.error(f"Failed to generate default output filename: {str(e)}")
        return None

def validate_output_directory(output_dir):
    if not os.path.exists(output_dir):
        raise NotADirectoryError(f"Invalid output path: Directory '{output_dir}' does not exist.")

    # Check for symbolic links
    if os.path.islink(output_dir):
        raise ValueError(f"Invalid output path: Symbolic link '{output_dir}' encountered.")

    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Invalid output path: No permission to write to directory '{output_dir}'.")

def check_filename_availability(filename):
    # Check if file exists
    if os.path.exists(filename):
        logging.warning(f"Output filename '{filename}' already exists. Overwriting...")

        # Ensure file is a regular file and not a directory or symbolic link
        if not stat.S_ISREG(os.stat(filename).st_mode):
            raise ValueError(f"Invalid output filename: '{filename}' is not a regular file.")

def main():
    parser = ArgumentParser(description="Compress files")
    parser.add_argument("-f", "--files", nargs="+", help="Filenames to compress (comma-separated string)")
    parser.add_argument("-o", "--output", help="Custom output filename")

    args = parser.parse_args()

    try:
        filenames = [f.strip() for f in args.files]

        # Validate input filenames
        if not all(isinstance(f, str) and os.path.exists(f) and os.path.isfile(f) for f in filenames):
            raise ValueError("Invalid input filename. Ensure all arguments are valid file paths.")

        output_filename = args.output
        if output_filename:
            check_filename_availability(output_filename)
        else:
            output_filename = get_default_output_filename(filenames)
            if not output_filename:
                logging.error("Failed to generate default output filename.")
                sys.exit(1)

        output_dir = os.path.dirname(output_filename)
        validate_output_directory(output_dir)

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
