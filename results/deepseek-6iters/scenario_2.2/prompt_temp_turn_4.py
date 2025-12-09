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

def get_validated_input(prompt, attempts=3):
    remaining_attempts = attempts
    while remaining_attempts > 0:
        user_input = input(prompt)
        try:
            validate_filename(user_input)
            return user_input
        except ValueError as e:
            print(str(e))
            remaining_attempts -= 1
            if remaining_attempts > 0:
                print(f"You have {remaining_attempts} attempts left. Please enter a valid file path.")
            else:
                raise ValueError("Invalid input. No more attempts allowed.")

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
    while True:
        try:
            filenames = []
            while True:
                filename = get_validated_input("Enter a file name to add to the archive (or type 'done' to finish): ")
                if filename.lower() == 'done':
                    break
                filenames.append(filename)

            archive_name = get_validated_input("Enter the archive name: ", attempts=1)
            compress_files(filenames, archive_name)
            break
        except ValueError as e:
            print(e)

if __name__ == "__main__":
    main()
