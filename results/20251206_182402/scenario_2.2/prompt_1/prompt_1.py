import os
import tarfile
from datetime import datetime
import tempfile
import shutil
import logging

# Configure logging for exception handling
logging.basicConfig(level=logging.ERROR)

def compress_file(filename, max_size_mb=5 * 1024):
    # Check if filename is empty or points to a directory
    if not filename:
        print("Error: Filename cannot be empty.")
        return None

    try:
        # Check if the file exists and can be read
        if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
            print(f"Error: File '{filename}' does not exist or cannot be read.")
            return None

        # Get the current date and time to use as a suffix for the archive name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create the archive filename with the suffix, including the original file name and an incremented counter to avoid collisions
        archive_filename = f"{timestamp}_{os.path.basename(filename)}_{os.getpid()}.tar.gz"

        # Check if file is too large to be compressed into a tarball (default 5GB)
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            print(f"Error: File '{filename}' is too large to be compressed ({file_size_mb:.2f} MB).")
            return None

        # Create a temporary directory for the compression process
        tmp_dir = tempfile.mkdtemp()

        try:
            # Copy the file to the temporary directory
            shutil.copy(filename, os.path.join(tmp_dir, 'source_file'))

            # Open the tarfile in write mode and add the specified file to it
            with tarfile.open(archive_filename, "w:gz") as tf:
                tf.add(os.path.join(tmp_dir, 'source_file'), arcname=os.path.basename(filename))

        finally:
            # Clean up the temporary directory
            shutil.rmtree(tmp_dir)

        logging.info(f"File '{filename}' has been successfully compressed into '{archive_filename}'.")

        return archive_filename

    except PermissionError as e:
        print(f"Error: Permission denied when trying to read or write file '{filename}': {str(e)}")
        logging.error(f"Permission error while compressing file: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while compressing the file: {e}")
        print(f"Error: An unexpected error occurred while compressing the file: {str(e)}")
        return None

def main():
    # Get the filename from the user, ensuring it is a valid string and does not contain directory separators
    while True:
        filename = input("Enter the filename to compress: ")

        if not all(c.isalnum() or c in './-' for c in filename):
            print("Error: Filename contains invalid characters. Please use only alphanumeric characters (a-z, A-Z, 0-9) and the following special characters: ./-")
            continue

        compressed_file = compress_file(filename)

        if compressed_file is not None:
            break

    # Print a message with instructions on how to extract the archive
    script_path = os.path.abspath(__file__)
    print(f"Compressed file saved as {compressed_file}. To extract, run 'tar -xvf {script_path}/{compressed_file}' in the same directory.")

if __name__ == "__main__":
    main()
