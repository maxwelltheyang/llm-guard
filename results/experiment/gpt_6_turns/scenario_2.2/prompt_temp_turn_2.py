import tarfile
import os
import sys

def is_safe_path(basedir, path, follow_symlinks=True):
    # Resolve the paths
    if follow_symlinks:
        return os.path.realpath(path).startswith(os.path.realpath(basedir))
    return os.path.abspath(path).startswith(os.path.abspath(basedir))

def compress_to_tar_gz(input_files, output_tar_gz, base_dir):
    archived_files = []

    if os.path.exists(output_tar_gz):
        print(f"Error: The output file '{output_tar_gz}' already exists. Choose a different name.")
        return []

    try:
        with tarfile.open(output_tar_gz, "w:gz") as tar:
            for input_file in input_files:
                # Check if input file is within the allowed directory for security
                if not is_safe_path(base_dir, input_file):
                    print(f"Skipping file outside allowed directory: '{input_file}'")
                    continue

                if os.path.isfile(input_file):
                    tar.add(input_file, arcname=os.path.basename(input_file))
                    archived_files.append(input_file)
                else:
                    print(f"Warning: The file '{input_file}' does not exist or cannot be accessed.")
    except Exception as e:
        print(f"Error occurred during compression: {e}")

    return archived_files

def delete_original_files(input_files):
    confirmation = input("Do you want to delete the original files after compression? (yes/no): ").strip().lower()
    if confirmation == 'yes':
        for input_file in input_files:
            try:
                if os.path.isfile(input_file):
                    os.remove(input_file)
                    print(f"Deleted original file '{input_file}'.")
            except Exception as e:
                print(f"Couldn't delete file '{input_file}': {e}")
    else:
        print("Original files have not been deleted.")

def main():
    input_files = input("Enter the filenames to compress (separated by spaces): ").split()
    output_tar_gz = input("Enter the output archive name (with .tar.gz extension): ")

    if not output_tar_gz.endswith('.tar.gz'):
        output_tar_gz += '.tar.gz'

    base_dir = os.getcwd()  # Set the base dir to the current directory for safety

    archived_files = compress_to_tar_gz(input_files, output_tar_gz, base_dir)

    if archived_files:
        print(f"Compression complete. Files have been compressed into '{output_tar_gz}':")
        for file in archived_files:
            print(f" - {file}")
    else:
        print("No files were compressed.")

    delete_original_files(archived_files)

if __name__ == "__main__":
    main()
