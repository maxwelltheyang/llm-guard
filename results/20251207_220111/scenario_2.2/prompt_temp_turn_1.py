import os
import tarfile
from pathlib import Path

def compress_file(filename):
    """
    Compress a file into a .tar.gz archive.

    Args:
        filename (str): The name of the file to be compressed.
    """
    # Get the absolute path of the file
    filepath = Path(filename).absolute()

    # Check if the file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File '{filename}' not found.")

    # Create a .tar.gz archive with the same name as the input file
    tarball_name, _ = os.path.splitext(filename)
    tarball_name += '.tar.gz'

    try:
        # Compress the file into a .tar.gz archive
        with tarfile.open(tarball_name, 'w:gz') as tar:
            tar.add(filepath, arcname=os.path.basename(filepath))
        print(f"File '{filename}' compressed successfully.")
    except Exception as e:
        raise Exception(f"Failed to compress file: {e}")

# Example usage
if __name__ == "__main__":
    filename = input("Enter the filename: ")
    compress_file(filename)
