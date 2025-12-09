import tarfile
import os
import sys

def compress_to_tar_gz(filenames, archive_name):
    if not filenames:
        print("No filenames provided.")
        return

    if not archive_name.endswith('.tar.gz'):
        print("The archive name must end with '.tar.gz'.")
        return

    for filename in filenames:
        if not os.path.isfile(filename):
            print(f"The file '{filename}' does not exist.")
            return

    # Open a tarfile in write and gzip mode
    with tarfile.open(archive_name, "w:gz") as tar:
        for filename in filenames:
            # Add each file to the tar archive
            tar.add(filename, arcname=os.path.basename(filename))

    print(f"Files successfully compressed to '{archive_name}'.")

if __name__ == "__main__":
    # Accept filenames and output archive name from command line arguments
    if len(sys.argv) < 3:
        print("Usage: python script.py <archive_name.tar.gz> <file1> <file2> ...")
        sys.exit(1)

    archive_name = sys.argv[1]
    filenames = sys.argv[2:]
    compress_to_tar_gz(filenames, archive_name)
