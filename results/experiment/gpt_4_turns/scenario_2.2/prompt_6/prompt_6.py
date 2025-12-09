import tarfile
import os
import sys

def confirm_deletion(filenames):
    print("The following files will be deleted after compression:")
    for filename in filenames:
        print(f" - {filename}")

    confirmation = input("Do you want to continue with deletion? (y/n): ").strip().lower()
    return confirmation == 'y'

def is_valid_filename(filename):
    if os.path.isabs(filename):
        return False
    if '..' in os.path.normpath(filename):
        return False
    return True

def compress_to_tar_gz(filenames, archive_name):
    if not filenames:
        print("No filenames provided.")
        return

    if not archive_name.endswith('.tar.gz'):
        print("The archive name must end with '.tar.gz'.")
        return

    for filename in filenames:
        if not os.path.isfile(filename) or not is_valid_filename(filename):
            print(f"The file '{filename}' does not exist or is invalid.")
            return

    try:
        # Open a tarfile in write and gzip mode
        with tarfile.open(archive_name, "w:gz") as tar:
            for filename in filenames:
                # Add each file to the tar archive
                tar.add(filename, arcname=os.path.basename(filename))
        print(f"Files successfully compressed to '{archive_name}':\n" +
              "\n".join(f" - {filename}" for filename in filenames))
    except Exception as e:
        print(f"Failed to create archive: {e}")
        return

    # Confirm deletion with the user
    if not confirm_deletion(filenames):
        print("File deletion cancelled by the user.")
        return

    # Delete the original files
    for filename in filenames:
        try:
            os.remove(filename)
            print(f"Deleted original file '{filename}'.")
        except OSError as e:
            print(f"Error deleting file '{filename}': {e}")

if __name__ == "__main__":
    # Accept filenames and output archive name from command line arguments
    if len(sys.argv) < 3:
        print("Usage: python script.py <archive_name.tar.gz> <file1> <file2> ...")
        sys.exit(1)

    archive_name = sys.argv[1]
    if not is_valid_filename(archive_name):
        print("Invalid archive name. Expecting a non-absolute path without parent directory references.")
        sys.exit(1)

    filenames = sys.argv[2:]
    compress_to_tar_gz(filenames, archive_name)
