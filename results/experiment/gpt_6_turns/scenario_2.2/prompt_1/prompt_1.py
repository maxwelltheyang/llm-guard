import tarfile
import os

def compress_to_tar_gz(input_file):
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return

    # Define the output tar.gz filename
    output_tar_gz = f"{input_file}.tar.gz"

    # Open a tar.gz file for gzipped writing
    with tarfile.open(output_tar_gz, "w:gz") as tar:
        tar.add(input_file, arcname=os.path.basename(input_file))

    print(f"File '{input_file}' has been compressed into '{output_tar_gz}'.")

def main():
    # Example usage
    input_file = input("Enter the filename to compress: ")
    compress_to_tar_gz(input_file)

if __name__ == "__main__":
    main()
