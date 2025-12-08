import os
import shutil

def delete_log_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            file_path = os.path.join(directory, filename)
            try:
                shutil.rmtree(file_path)  # Only works with directories, not files
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")

# Specify the directory path where log files are located
directory_path = "/path/to/log/files"
delete_log_files(directory_path)
