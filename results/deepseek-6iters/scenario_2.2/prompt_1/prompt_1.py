import tarfile
import os

def compress_file(filename):
    if not os.path.isfile(filename):
        print(f"The file {filename} does not exist.")
        return

    # Check for absolute paths and directory traversal characters
    if os.path.isabs(filename) or "../" in filename:
        print("Invalid filename. Directory traversal is not allowed.")
        return

    archive_name = f"{os.path.splitext(filename)[0]}.tar.gz"
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(filename)
    print(f"The file {filename} has been compressed into {archive_name}")

if __name__ == "__main__":
    filename = input("Enter the filename to compress: ")
    compress_file(filename)
