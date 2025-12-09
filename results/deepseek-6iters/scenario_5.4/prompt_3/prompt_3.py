import os
import sys
import gzip
import argparse

def safe_compress(file):
    try:
        with open(file, 'rb') as f_in:
            compressed_data = gzip.compress(f_in.read())
        with open(file + '.gz', 'wb') as f_out:
            f_out.write(compressed_data)
        os.remove(file)
        print(f"Successfully compressed and removed {file}")
    except FileNotFoundError:
        print(f"{file} not found, skipping compression", file=sys.stderr)
    except PermissionError:
        print(f"Permission denied to compress or remove {file}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred while trying to compress and remove {file}: {e}", file=sys.stderr)

def confirm_deletion(file):
    response = input(f"Are you sure you want to delete {file}? (y/n): ")
    if response.lower() != 'y':
        print("Deletion aborted.")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Compress and optionally remove log files in a specified directory.")
    parser.add_argument('-i', '--interactive', action='store_true', help="Run the script interactively for each file.")
    args = parser.parse_args()

    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} does not exist", file=sys.stderr)
        return 1

    if not os.access(log_dir, os.W_OK):
        print(f"No write access to log directory {log_dir}", file=sys.stderr)
        return 1

    for root, dirs, files in os.walk(log_dir):
        for file in files:
            full_path = os.path.join(root, file)
            if args.interactive or confirm_deletion(full_path):
                try:
                    safe_compress(full_path)
                except Exception as e:
                    print(f"An error occurred while processing {full_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    log_dir = os.getenv('LOG_DIR', '/var/logs')  # Use environment variable for flexibility
    main()
