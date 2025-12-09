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
        raise ValueError("The provided file does not exist.")
    if p.is_absolute() or '..' in str(p) or not all(c in '/.' for c in filename):
        logger.error(f"Invalid filename: {filename}")
        raise ValueError("Invalid filename. Please ensure the path is valid and secure.")
    return True

def get_validated_input(prompt):
    while True:
        user_input = input(prompt)
        try:
            validate_filename(user_input)
            return user_input
        except ValueError as e:
            print(str(e))
            print("Please enter a valid file path.")

def compress_files(filenames, archive_name):
    errors = []
    with tarfile.open(archive_name, "w") as tar:
        for filename in filenames:
            try:
                file_path = Path(filename).resolve()
                if not os.path.exists(file_path):
                    logger.error(f"File {file_path} does not exist.")
                    raise FileNotFoundError(f"The file or directory '{file_path}' does not exist.")
                tar.add(file_path, arcname=Path(filename).name)
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
    archive_name = get_validated_input(prompt) or 'output.tar'

    filenames = []
    while True:
        filename = input("Enter a filename to add to the archive or type 'done' to finish: ")
        if filename == 'done':
            break
        try:
            validate_filename(filename)
            filenames.append(filename)
        except ValueError as e:
            print(str(e))
            print("Please enter a valid file path.")

    compress_files(filenames, archive_name)

if __name__ == "__main__":
    main()
