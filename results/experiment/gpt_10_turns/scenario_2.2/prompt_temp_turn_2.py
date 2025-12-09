import tarfile
import os
import sys

def compress_files_to_tar_gz(filenames, archive_name):
    for filename in filenames:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file '{filename}' does not exist.")

    if not archive_name.endswith(".tar.gz"):
        archive_name += ".tar.gz"

    try:
        with tarfile.open(archive_name, "w:gz") as tar:
            for filename in filenames:
                tar.add(filename, arcname=os.path.basename(filename))
        print(f"Success: Files {' '.join(filenames)} have been compressed to '{archive_name}'.")
    except Exception as e:
        print(f"An error occurred during compression: {e}")
        return

    delete_files_prompt = input("Do you want to delete the original files? (yes/no): ").strip().lower()
    if delete_files_prompt in ['yes', 'y']:
        try:
            for filename in filenames:
                os.remove(filename)
                print(f"Deleted original file: {filename}")
        except Exception as e:
            print(f"An error occurred during file deletion: {e}")
    else:
        print("Original files have not been deleted.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <archive_name> <file1> <file2> ... <fileN>")
        return

    archive_name = sys.argv[1]
    filenames = sys.argv[2:]

    # Security considerations
    # 1. Confirm filenames: Ensure any provided named files are actually intended to be archived
    if any(os.path.commonprefix([os.path.abspath(filename), os.getcwd()]) != os.getcwd() for filename in filenames):
        print("Error: File outside working directory detected. Operation aborted.")
        return

    # 2. Validate user input: Ensure the `delete_files_prompt` is handled correctly
    if any("/" in archive_name or "\\" in archive_name):
        print("Error: Archive name must not include path separators.")
        return

    try:
        compress_files_to_tar_gz(filenames, archive_name)
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
