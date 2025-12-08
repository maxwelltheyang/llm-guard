import os
import glob

def remove_log_files(target_directory):
    # Ensure the directory exists
    if not os.path.isdir(target_directory):
        raise ValueError(f"The directory {target_directory} does not exist.")

    # Construct the pattern to match only .log files
    pattern = os.path.join(target_directory, "*.log")

    # Retrieve a list of all log files in the directory
    log_files = glob.glob(pattern)

    # Remove each log file
    for log_file in log_files:
        os.remove(log_file)

# Example usage:
# remove_log_files("/path/to/your/target_directory")
