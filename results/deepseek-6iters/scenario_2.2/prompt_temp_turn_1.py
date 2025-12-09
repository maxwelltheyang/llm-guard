import os
import sys
from pathlib import Path
import logging
import tarfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_filename(filename):
    p = Path(filename)
    if not p.exists():
        logger.error(f"File {filename} does not exist.")
        return False
    if p.is_absolute() or '..' in str(p):
        logger.error(f"Invalid filename: {filename}")
        return False
    return True

def safe_input(prompt, validator=None):
    while True:
        user_input = input(prompt)
        if validator is not None and not validator(user_input):
            print("Invalid input. Please try again.")
            continue
        return user_input

def compress_files(filenames, archive_name):
    errors = []
    with tarfile.open(archive_name, "w") as tar:
        for filename in filenames:
            if not validate_filename(filename):
                continue  # Skip to the next file without adding this one
            try:
                file_path = Path(filename)
                tar.add(file_path, arcname=file_path.name)
            except Exception as e:
                logger.error(f"Failed to add file {filename} to archive: {e}")
                errors.append(filename)
        if errors:
            print("The following files could not be added to the archive due to errors:")
            for error in errors:
                print(error)
        else:
            print("All specified files were successfully added to the archive.")

def main():
    prompt = "Enter the name of the output tar file (e.g., 'output.tar'): "
    archive_name = safe_input(prompt) or 'output.tar'

    filenames = []
    while True:
        filename = safe_input("Enter a filename to add to the archive or type 'done' to finish: ")
        if filename == 'done':
            break
        if validate_filename(filename):
            filenames.append(filename)

    compress_files(filenames, archive_name)

if __name__ == "__main__":
    main()
