import tarfile
import os

def compress_files_to_tar_gz(filenames):
    for filename in filenames:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file '{filename}' does not exist.")

    # Create a tar.gz archive name based on the first input filename
    archive_name = "compressed_files.tar.gz"

    # Open a tarfile object in write mode with gzip compression
    with tarfile.open(archive_name, "w:gz") as tar:
        for filename in filenames:
            # Add each file to the archive
            tar.add(filename, arcname=os.path.basename(filename))

    print(f"Files {' '.join(filenames)} have been compressed to '{archive_name}'.")

def main():
    filenames = input("Enter the filenames to compress (separated by spaces): ").split()
    try:
        compress_files_to_tar_gz(filenames)
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
