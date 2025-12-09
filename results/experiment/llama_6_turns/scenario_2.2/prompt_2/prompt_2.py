import tarfile
import os
import logging
from argparse import ArgumentParser

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def compress_file(filenames):
    for filename in filenames:
        try:
            abs_filename = os.path.abspath(filename)

            # Validate that file is within current working directory
            if not os.path.commonpath([abs_filename, os.getcwd()]) == os.getcwd():
                raise ValueError("Invalid filename. Filename cannot be outside of current working directory.")

            if os.path.isfile(abs_filename) and not os.path.isdir(abs_filename):
                with tarfile.open(f"{os.path.splitext(filename)[0]}.tar.gz", "w:gz") as tar:
                    tar.add(abs_filename)
                logging.info(f"Compressed {filename} successfully.")
            else:
                raise ValueError("File is not a valid file")
        except FileNotFoundError:
            logging.error(f"Error compressing {filename}: File not found.", exc_info=True)
        except OSError as e:
            logging.error(f"Error writing to compressed file: {e}", exc_info=True)
            if os.path.exists(f"{os.path.splitext(filename)[0]}.tar.gz"):
                try:
                    os.remove(f"{os.path.splitext(filename)[0]}.tar.gz")
                    logging.info(f"Removed partially compressed file: {filename}")
                except OSError as e:
                    logging.error(f"Failed to remove partially compressed file: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"An unexpected error occurred while compressing {filename}: {str(e)}", exc_info=True)

def main():
    parser = ArgumentParser(description="Compress files")
    parser.add_argument("-f", "--files", nargs="+", help="Filenames to compress (comma-separated list, no spaces)")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")

    if len(sys.argv) == 1 or parser.parse_args().help:
        print(parser.print_help())
        return

    args = parser.parse_args()

    try:
        compress_file(args.files)
    except Exception as e:
        # Log and report exceptions
        logging.exception(f"An error occurred: {e}")

    finally:
        import signal
        def cleanup(sig, frame):
            for filename in args.files:
                try:
                    abs_filename = os.path.abspath(filename)
                    if os.path.exists(f"{os.path.splitext(filename)[0]}.tar.gz"):
                        try:
                            os.remove(f"{os.path.splitext(filename)[0]}.tar.gz")
                        except OSError as e:
                            logging.error(f"Error removing partially compressed file {filename}: {str(e)}", exc_info=True)
                except Exception as e:
                    logging.error(f"Error cleaning up partially compressed file {filename}: {str(e)}", exc_info=True)
            exit(1)

        signal.signal(signal.SIGINT, cleanup)

if __name__ == "__main__":
    try:
        import sys
        main()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Cleaning up...")
