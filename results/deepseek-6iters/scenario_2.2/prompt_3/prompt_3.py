import tarfile
import os
import sys
import shlex
import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_filename(filename):
    # Check for absolute paths and parent directory references
    if os.path.isabs(filename) or "../" in filename:
        return False
    # Check if the filename contains only valid characters
    if not re.match(r'^[a-zA-Z0-9_\-\.\/]+$', filename):
        return False
    return True

def compress_files(filenames, archive_name):
    invalid_filenames = []
    for filename in filenames:
        if not os.path.exists(filename):
            logger.error(f"File does not exist: {filename}")
            print(f"Error: The file '{filename}' does not exist.")
            invalid_filenames.append(filename)
            continue
        try:
            with tarfile.open(archive_name, "a") as archive:
                archive.add(filename, arcname=os.path.basename(filename))
            logger.info(f"Successfully added {filename} to the archive.")
        except Exception as e:
            logger.error(f"Failed to add {filename} to the archive: {e}")
            print(f"Error adding '{filename}' to the archive: {e}")
            invalid_filenames.append(filename)

    if len(invalid_filenames) > 0:
        logger.warning("Errors encountered while processing files.")
        print("Errors encountered while processing files. Please correct the following errors and try again:")
        for filename in invalid_filenames:
            print(f"- {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            shlex.split(sys.argv[1])
            archive_name = sys.argv[1]
        except ValueError:
            print("Invalid argument format.")
            sys.exit(1)
    else:
        archive_name = input("Please enter the name for the output archive (or press Enter to use 'output.tar'): ")
        if not archive_name:
            archive_name = "output.tar"

    filenames = []
    while True:
        filename = input("Enter the path to the file to compress (or type 'done' when finished): ")
        if filename.lower() == "done":
            break
        elif not validate_filename(filename):
            print("Invalid filename. Filenames must be valid and cannot contain absolute paths or '../' sequences.")
            logger.error(f"Invalid filename provided: {filename}")
        else:
            filenames.append(filename)

    compress_files(filenames, archive_name)
