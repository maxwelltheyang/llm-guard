import tarfile
import os
import sys

def compress_to_tar_gz(filenames):
    if not filenames:
        print("No filenames provided.")
        return

    for filename in filenames:
        if not os.path.isfile(filename):
            print(f"The file '{filename}' does not exist.")
            return

    # Construct the archive name
    archive_name = "archive.tar.gz"

    # Open a tarfile in write and gzip mode
    with tarfile.open(archive_name, "w:gz") as tar:
        for filename in filenames:
            # Add each file to the tar archive
            tar.add(filename, arcname=os.path.basename(filename))

    print(f"Files successfully compressed to '{archive_name}'.")

if __name__ == "__main__":
    # Accept filenames from command line arguments
    filenames = sys.argv[1:]
    compress_to_tar_gz(filenames)
