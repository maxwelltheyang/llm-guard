import tarfile
import os
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def compress_file(filename):
    try:
        abs_filename = os.path.abspath(filename)

        # Validate that file is within current working directory
        if not os.path.commonpath([abs_filename, os.getcwd()]) == os.getcwd():
            raise ValueError("Invalid filename. Filename cannot be outside of current working directory.")

        if os.path.isfile(abs_filename) and not os.path.isdir(abs_filename):
            with tarfile.open(f"{filename}.tar.gz", "w:gz") as tar:
                tar.add(abs_filename)
            logging.info(f"Compressed {filename} successfully.")
        else:
            raise ValueError("File is not a valid file")
    except FileNotFoundError:
        logging.error(f"Error compressing {filename}: File not found.", exc_info=True)
    except OSError as e:
        logging.error(f"Error writing to compressed file: {e}", exc_info=True)
        if os.path.exists(f"{filename}.tar.gz"):
            try:
                os.remove(f"{filename}.tar.gz")
                logging.info(f"Removed partially compressed file: {filename}.tar.gz")
            except OSError as e:
                logging.error(f"Failed to remove partially compressed file: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred while compressing {filename}: {str(e)}", exc_info=True)

def main():
    filename = input("Enter the filename to compress: ")

    try:
        compress_file(filename)
    except Exception as e:
        # Log and report exceptions
        logging.exception(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.")
