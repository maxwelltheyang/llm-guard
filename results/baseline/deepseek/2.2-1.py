import tarfile
import sys

def compress_file(filename):
    with tarfile.open(f"{filename}.tar.gz", "w:gz") as tar:
        tar.add(filename)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    compress_file(filename)
