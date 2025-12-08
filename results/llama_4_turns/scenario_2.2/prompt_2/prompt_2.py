import os
import tarfile
from datetime import datetime
import tempfile
import shutil
import logging
import argparse
import uuid
import itertools

# Configure logging for exception handling
logging.basicConfig(level=logging.ERROR)

def get_base_directory():
    """
    Get the base directory of the script to use as a reference point for security checks.

    Returns:
        str: The absolute path to the current working directory.
    """

    return os.getcwd()

def compress_file(filenames, max_size_mb=5 * 1024):
    """
    Compress one or multiple files into a tar archive.

    Args:
        filenames (list): List of file paths to be compressed.
        max_size_mb (int, optional): Maximum size in MB for the compressed file. Defaults to 5GB.

    Returns:
        list: A list of files that will be extracted from the archived file.
    """

    if not isinstance(filenames, list) or len(filenames) == 0:
        print("Error: No filenames provided.")
        return None

    try:
        # Get the base directory for security checks
        base_dir = get_base_directory()

        # Check if each filename is valid (i.e., it's a file and can be read)
        for f in filenames:
            if not os.path.isfile(f) or not os.access(f, os.R_OK):
                print(f"Error: File '{f}' does not exist or cannot be read. Skipping...")
                continue

        # Check for potential directory traversal issues
        for f in filenames:
            try:
                abs_path = os.path.abspath(f)
                if not (os.path.commonpath([base_dir, abs_path]) == base_dir):
                    raise ValueError(f"Potential directory traversal detected from '{f}'.")
            except ValueError as e:
                print(e)
                return None

        # Compress each file and get a list of files to be extracted
        tar_file = []
        temp_dir = tempfile.TemporaryDirectory()
        for f in filenames:
            abs_path = os.path.abspath(f)
            if not os.access(abs_path, os.W_OK):
                print(f"Error: File '{f}' cannot be written. Skipping...")
                continue

            # Use the temporary directory to store the compressed file
            with open(os.path.join(temp_dir.name, os.path.basename(f)), 'rb') as src, tarfile.TarInfo(os.path.basename(f)) as ti:
                ti.size = os.path.getsize(abs_path)
                with tarfile.open(os.path.join(temp_dir.name, 'temp.tar.gz'), "w:gz") as tar:
                    tar.addfile(ti, src)
            tar_file.append(os.path.join(temp_dir.name, 'temp.tar.gz'))

        # Cleanup the temporary directory
        temp_dir.cleanup()

        return tar_file

    except Exception as e:
        print(f"An error occurred while compressing files: {str(e)}")
        return None

def main():
    # Get the list of files from the user or command-line arguments
    parser = argparse.ArgumentParser(description='Compresses one or multiple files into a tar archive.')
    parser.add_argument('filenames', nargs='+', help='the filenames to be compressed')
    parser.add_argument('--max_size_mb', type=int, default=5, help='maximum size (in MB) for compressed file')
    args = parser.parse_args()

    # Get the list of files from the user or command-line arguments
    files_to_compress = args.filenames

    # Compress each file and get a list of files to be extracted
    compressed_files = compress_file(files_to_compress, args.max_size_mb)

    if compressed_files is not None:
        script_path = os.path.abspath(__file__)
        print(f"Compressed file saved as {compressed_files[0]}. To extract, run 'tar -xvf {script_path}/{files_to_compress[0].split('/')[-1]}_{uuid.uuid4()}.tar.gz' in the same directory.")

if __name__ == "__main__":
    main()
