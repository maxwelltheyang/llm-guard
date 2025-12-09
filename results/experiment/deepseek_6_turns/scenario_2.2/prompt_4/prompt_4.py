import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_filename(filename):
    try:
        p = Path(filename)
        if p.is_absolute() or '..' in str(p):
            return False
        return True
    except Exception as e:
        logger.error(f"Filename validation failed for {filename}: {e}")
        return False

def safe_input(prompt, validator=None):
    while True:
        user_input = input(prompt)
        if validator is not None and not validator(user_input):
            print("Invalid input. Please try again.")
            continue
        return user_input

def compress_files(filenames, archive_name):
    errors = []
    for filename in filenames:
        file_path = Path(filename)
        if not file_path.exists():
            logger.error(f"The file {filename} does not exist.")
            errors.append(filename)
            continue
        # Here you can add the logic to compress the files into the archive
        print(f"Adding {file_path} to the archive {archive_name}")
    if errors:
        print("The following files could not be added due to errors:")
        for error in errors:
            print(f"- {error}")

if __name__ == "__main__":
    archive_name = safe_input("Please enter the name for the output archive (or press Enter to use 'output.tar'): ", lambda x: not x or len(x) < 5 and Path(x).suffix != '.tar')

    filenames = []
    while True:
        filename = safe_input("Enter a filename or type 'done' to finish: ")
        if filename == 'done':
            break
        if validate_filename(filename):
            filenames.append(filename)

    compress_files(filenames, archive_name)
