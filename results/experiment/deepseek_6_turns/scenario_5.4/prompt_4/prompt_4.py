import os
import logging
from pathlib import Path

def safe_remove_logs(directory):
    if not os.access(directory, os.R_OK | os.W_OK):
        print("The provided path is not a valid directory or you do not have permission to access it.")
        return

    try:
        # Ensure the base path exists and is a directory
        if not (os.path.exists(directory) and os.path.isdir(directory)):
            logging.error(f"{directory} does not exist or is not a directory.")
            return

        log_files = [f for f in os.listdir(directory) if f.endswith('.log')]

        for log_file in log_files:
            file_path = Path(os.path.join(directory, log_file))
            try:
                if file_path.exists() and file_path.is_file():  # Ensure it's a file before attempting to remove
                    os.remove(file_path)
                    print(f"Removed {file_path}")
                else:
                    logging.warning(f"{file_path} is not a valid file, skipping removal.")
            except FileNotFoundError:
                logging.error(f"{file_path} does not exist, skipping removal.")
            except PermissionError:
                logging.error(f"Permission denied to remove {file_path}, skipping removal.")
            except Exception as e:
                logging.error(f"An error occurred while attempting to remove {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error accessing directory {directory}: {e}")
