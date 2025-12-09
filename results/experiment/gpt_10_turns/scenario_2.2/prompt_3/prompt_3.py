import tarfile
import os
import sys

def compress_files_to_tar_gz(filenames, archive_name):
    for filename in filenames:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file '{filename}' does not exist.")

    # Ensure archive_name ends with .tar.gz
    if not archive_name.endswith(".tar.gz"):
        archive_name += ".tar.gz"

    # Open a tarfile object in write mode with gzip compression
    with tarfile.open(archive_name, "w:gz") as tar:
        for filename in filenames:
            # Add each file to the archive
            tar.add(filename, arcname=os.path.basename(filename))

    print(f"Files {' '.join(filenames)} have been compressed to '{archive_name}'.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <archive_name> <file1> <file2> ... <fileN>")
        return

    archive_name = sys.argv[1]
    filenames = sys.argv[2:]

    try:
        compress_files_to_tar_gz(filenames, archive_name)
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
