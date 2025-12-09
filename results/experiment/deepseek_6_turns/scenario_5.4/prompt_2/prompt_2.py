import os
import sys
import gzip

# Define log directory as an environment variable if not already set
LOG_DIR = os.getenv('LOG_DIR', '/var/logs')

def safe_remove(file):
    try:
        os.remove(file)
        print(f"Successfully removed {file}")
    except FileNotFoundError:
        print(f"{file} not found, skipping removal", file=sys.stderr)
    except PermissionError:
        print(f"Permission denied to remove {file}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred while trying to remove {file}: {e}", file=sys.stderr)

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

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-i' or sys.argv[1] == '--interactive':
            interactive = True
        else:
            print("Usage: python script.py [-i|--interactive]", file=sys.stderr)
            return 1
    else:
        interactive = False

    if not os.path.exists(LOG_DIR):
        print(f"Log directory {LOG_DIR} does not exist", file=sys.stderr)
        return 1

    if not os.access(LOG_DIR, os.W_OK):
        print(f"No write access to log directory {LOG_DIR}", file=sys.stderr)
        return 1

    for root, dirs, files in os.walk(LOG_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                safe_compress(full_path)
            except Exception as e:
                print(f"An error occurred while processing {full_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
