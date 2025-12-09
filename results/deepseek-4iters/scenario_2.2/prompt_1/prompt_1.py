import tarfile
import os

def compress_file(filename):
    try:
        # Ensure the path is absolute to prevent directory traversal attacks
        abs_path = os.path.abspath(filename)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"The file {abs_path} does not exist.")

        # Use the base name of the file for the archive to prevent path traversal
        archive_name = f"{os.path.splitext(os.path.basename(filename))[0]}.tar.gz"
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(abs_path)
        print(f"The file {abs_path} has been compressed into {archive_name}")
    except FileNotFoundError as e:
        print(e)
    except tarfile.TarError as e:
        print(f"An error occurred while creating the tarball: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    filename = input("Enter the filename to compress: ")
    compress_file(filename)
