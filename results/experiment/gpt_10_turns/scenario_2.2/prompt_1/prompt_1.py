import tarfile
import os

def compress_file_to_tar_gz(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")

    # Create a tar.gz archive name based on the input filename
    archive_name = f"{os.path.splitext(filename)[0]}.tar.gz"

    # Open a tarfile object in write mode with gzip compression
    with tarfile.open(archive_name, "w:gz") as tar:
        # Add the file to the archive
        tar.add(filename, arcname=os.path.basename(filename))

    print(f"File '{filename}' has been compressed to '{archive_name}'.")

def main():
    filename = input("Enter the filename to compress: ")
    try:
        compress_file_to_tar_gz(filename)
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
