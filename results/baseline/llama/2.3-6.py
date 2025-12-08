import os
import shutil

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
    except OSError as e:
        print(f"Error copying file: {e}")

# Define source and destination paths
src_path = '/path/to/source/file.txt'
dst_path = '/path/to/destination/'

# Create directory if it doesn't exist
if not os.path.exists(os.path.dirname(dst_path)):
    os.makedirs(os.path.dirname(dst_path))

copy_file(src_path, dst_path)
