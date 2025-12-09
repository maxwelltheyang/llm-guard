import tarfile
import os

def compress_to_tar_gz(input_files, output_tar_gz):
    archived_files = []

    # Validate file paths to avoid directory traversal attacks
    for input_file in input_files:
        if not os.path.isabs(input_file) and '..' in input_file:
            print(f"Skipping potentially unsafe file path: '{input_file}'")
            continue

        if os.path.isfile(input_file):
            with tarfile.open(output_tar_gz, "w:gz") as tar:
                tar.add(input_file, arcname=os.path.basename(input_file))
            archived_files.append(input_file)
        else:
            print(f"Warning: The file '{input_file}' does not exist or cannot be accessed.")

    return archived_files

def delete_original_files(input_files):
    confirmation = input("Do you want to delete the original files after compression? (yes/no): ").strip().lower()
    if confirmation == 'yes':
        for input_file in input_files:
            if os.path.isfile(input_file):
                os.remove(input_file)
                print(f"Deleted original file '{input_file}'.")
    else:
        print("Original files have not been deleted.")

def main():
    input_files = input("Enter the filenames to compress (separated by spaces): ").split()
    output_tar_gz = input("Enter the output archive name (with .tar.gz extension): ")

    # Validate the output tar.gz file path
    if not output_tar_gz.endswith('.tar.gz'):
        output_tar_gz += '.tar.gz'
    if '..' in output_tar_gz or os.path.isabs(output_tar_gz):
        print("Error: Invalid output file path. Avoid using absolute paths or relative paths with '..'.")
        return

    archived_files = compress_to_tar_gz(input_files, output_tar_gz)

    if archived_files:
        print(f"Compression complete. Files have been compressed into '{output_tar_gz}':")
        for file in archived_files:
            print(f" - {file}")
    else:
        print("No files were compressed.")

    delete_original_files(archived_files)

if __name__ == "__main__":
    main()
