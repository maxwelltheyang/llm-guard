import os

def safe_remove_logs(directory):
    if not os.path.isdir(directory):
        print("The specified directory does not exist.")
        return

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.log'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Removed {file_path}")
                except Exception as e:
                    print(f"Failed to remove {file_path}: {e}")

# Example usage:
safe_remove_logs('/path/to/log/directory')
