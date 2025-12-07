import tarfile
import os

def compress_file(filename):
    with tarfile.open(f"{filename}.tar.gz", "w:gz") as tar:
        tar.add(filename)

if __name__ == "__main__":
    filename = input("Enter the filename to be compressed: ")
    try:
        compress_file(filename)
        print(f"Compression of {filename} complete.")
    except Exception as e:
        print(f"Error: {e}")
