import tarfile
import os

def compress_to_tar_gz(input_files):
    # Define the output tar.gz filename (using a generic name)
    output_tar_gz = "archive.tar.gz"

    # Open a tar.gz file for gzipped writing
    with tarfile.open(output_tar_gz, "w:gz") as tar:
        for input_file in input_files:
            # Check if the input file exists
            if os.path.isfile(input_file):
                tar.add(input_file, arcname=os.path.basename(input_file))
                print(f"Added '{input_file}' to '{output_tar_gz}'.")
            else:
                print(f"Warning: The file '{input_file}' does not exist and will be skipped.")

    print(f"Compression complete. Files have been compressed into '{output_tar_gz}'.")

def main():
    # Example usage
    input_files = input("Enter the filenames to compress (separated by spaces): ").split()
    compress_to_tar_gz(input_files)

if __name__ == "__main__":
    main()
