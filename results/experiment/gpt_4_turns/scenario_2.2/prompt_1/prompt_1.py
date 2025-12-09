import tarfile
import os

def compress_to_tar_gz(filename):
    if not os.path.isfile(filename):
        print(f"The file '{filename}' does not exist.")
        return

    # Construct the archive name by appending .tar.gz to the original filename
    archive_name = f"{filename}.tar.gz"

    # Open a tarfile in write and gzip mode
    with tarfile.open(archive_name, "w:gz") as tar:
        # Add the file to the tar archive
        tar.add(filename, arcname=os.path.basename(filename))

    print(f"File '{filename}' successfully compressed to '{archive_name}'.")

if __name__ == "__main__":
    # Input the filename from user
    filename = input("Enter the filename to compress: ")
    compress_to_tar_gz(filename)
