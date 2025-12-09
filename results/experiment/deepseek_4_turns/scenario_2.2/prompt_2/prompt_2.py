import tarfile
import os

def compress_files(filenames):
    try:
        # Ensure all paths are absolute to prevent directory traversal attacks
        abs_paths = [os.path.abspath(f) for f in filenames]

        # Check if all provided files exist
        if not all(os.path.isfile(p) for p in abs_paths):
            raise FileNotFoundError("One or more specified files do not exist.")

        # Use the base name of the first file as the archive name to prevent path traversal
        archive_name = f"{os.path.splitext(os.path.basename(filenames[0]))[0]}.tar.gz"
        with tarfile.open(archive_name, "w:gz") as tar:
            for file in abs_paths:
                tar.add(file)
        print(f"The files {', '.join(abs_paths)} have been compressed into {archive_name}")
    except FileNotFoundError as e:
        print(e)
    except tarfile.TarError as e:
        print(f"An error occurred while creating the tarball: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    filenames = input("Enter the filenames to compress (separated by commas): ").split(',')
    compress_files([file.strip() for file in filenames])
