import os
import sys
from pathlib import Path
import tarfile
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_filename(filename):
    try:
        file_path = Path(filename).resolve()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file or directory '{file_path}' does not exist.")
        if os.path.isdir(file_path) and any(Path(d).parts[-1] == '..' for d in [file_path, filename]):
            raise ValueError("Invalid path: Contains invalid component '..', which is potentially dangerous.")
        return True
    except Exception as e:
        logging.error(f"Failed to validate file {filename}: {e}")
        raise ValueError(str(e))

def get_validated_input(prompt, attempts=3):
    remaining_attempts = attempts
    while remaining_attempts > 0:
        user_input = input(prompt)
        try:
            if validate_filename(user_input):
                return user_input
            else:
                raise ValueError("Invalid input. Please enter a valid file or directory path.")
        except ValueError as e:
            remaining_attempts -= 1
            if remaining_attempts > 0:
                print(f"Error: {e}. You have {remaining_attempts} attempts left.")
            else:
                raise ValueError("Maximum number of attempts reached. Please provide a valid input.")

def compress_files(filenames, archive_name):
    errors = []
    with tarfile.open(archive_name, "w") as tar:
        for filename in filenames:
            try:
                file_path = Path(filename).resolve()
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"The file or directory '{file_path}' does not exist.")
                tar.add(file_path, arcname=Path(filename).name)
            except Exception as e:
                logging.error(f"Failed to add file {filename} to archive: {e}")
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

            archive_name = get_validated_input("Enter the archive name (leave blank for default 'output.tar'): ", attempts=1)
            if not archive_name:
                archive_name = "output.tar"

            compress_files(filenames, archive_name)
            break
        except ValueError as e:
            print(e)

if __name__ == "__main__":
    main()
