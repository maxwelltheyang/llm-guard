import tarfile
import os

def compress_file(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")

    # Get the directory and base name of the file
    dir_name = os.path.dirname(filename)
    base_name = os.path.basename(filename)

    # Create a tarfile with the same basename in the same directory
    archive_name = os.path.join(dir_name, f"{os.path.splitext(base_name)[0]}.tar.gz")

    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(filename, arcname=base_name)

if __name__ == "__main__":
    filename = input("Enter the filename to compress: ")
    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file '{filename}' does not exist.")

        compress_file(filename)
        print(f"The file '{filename}' has been compressed into '{os.path.splitext(filename)[0]}.tar.gz'.")
    except FileNotFoundError as e:
        print(f"Error: The file you provided does not exist or is not a valid file path. Please check and try again.")
