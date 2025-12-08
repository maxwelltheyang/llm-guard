import tarfile
import os

def compress_file_to_tar_gz(input_filename):
    output_filename = f"{input_filename}.tar.gz"
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(input_filename, arcname=os.path.basename(input_filename))

if __name__ == "__main__":
    filename = input("Enter the filename to compress: ")
    compress_file_to_tar_gz(filename)
    print(f"File compressed to {filename}.tar.gz")
