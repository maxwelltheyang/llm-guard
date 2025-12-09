import tarfile
import os

def compress_to_tar_gz(input_files, output_tar_gz):
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

def delete_original_files(input_files):
    # Ask for user confirmation
    confirmation = input("Do you want to delete the original files after compression? (yes/no): ").strip().lower()
    if confirmation == 'yes':
        for input_file in input_files:
            if os.path.isfile(input_file):
                os.remove(input_file)
                print(f"Deleted original file '{input_file}'.")
    else:
        print("Original files have not been deleted.")

def main():
    # Example usage
    input_files = input("Enter the filenames to compress (separated by spaces): ").split()
    output_tar_gz = input("Enter the output archive name (with .tar.gz extension): ")

    # Validate the output filename extension
    if not output_tar_gz.endswith('.tar.gz'):
        output_tar_gz += '.tar.gz'

    # Compress files
    compress_to_tar_gz(input_files, output_tar_gz)

    # Ask and delete original files if confirmed
    delete_original_files(input_files)

if __name__ == "__main__":
    main()
