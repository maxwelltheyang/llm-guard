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

            with tarfile.open(output_filename, "w:gz") as tar:
                tar.add(abs_filename)
            logging.info(f"Compressed {filename} successfully.")
        except FileNotFoundError:
            logging.error(f"Error compressing {filename}: File not found.", exc_info=True)
        except OSError as e:
            logging.error(f"Error writing to compressed file: {e}", exc_info=True)
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
        raise ValueError(f"Failed to generate default output filename: {str(e)}")

def check_filename_availability(output_filename):
    existing_file = os.path.join(os.path.dirname(output_filename), os.path.basename(output_filename))
    if os.path.exists(existing_file) and not os.path.samefile(output_filename, existing_file):
        raise ValueError(f"Output filename '{output_filename}' already exists as a file or directory.")

def validate_output_directory(output_dir):
    try:
        if not os.access(output_dir, os.W_OK):
            raise PermissionError("No permission to write to output directory")
    except OSError as e:
        raise Exception(f"Invalid output directory: {str(e)}")

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
