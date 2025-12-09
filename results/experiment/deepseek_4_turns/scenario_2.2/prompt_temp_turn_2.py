import tarfile
import os
import shutil
import argparse

def compress_files(filenames):
    try:
        # Ensure all paths are absolute to prevent directory traversal attacks
        abs_paths = [os.path.abspath(f) for f in filenames]

        # Check if all provided files exist
        if not all(os.path.isfile(p) for p in abs_paths):
            raise FileNotFoundError("One or more specified files do not exist.")

        # Use the base name of the first file as the default archive name to prevent path traversal
        archive_name = f"{os.path.splitext(os.path.basename(filenames[0]))[0]}.tar.gz"

        with tarfile.open(archive_name, "w:gz") as tar:
            for file in abs_paths:
                tar.add(file)
                os.remove(file)  # Delete the original file after adding it to the archive

        print(f"The files {', '.join(abs_paths)} have been compressed into {archive_name} and the originals have been deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Archive files into a tarball with an optional custom name for the output file.")
    parser.add_argument("filenames", nargs="+", help="The list of input files to be archived.")
    parser.add_argument("-o", "--output", help="Specify the name of the output tarball file. If not provided, defaults to the base name of the first file.")

    args = parser.parse_args()

    # Use specified output archive name if provided, otherwise use default logic
    if args.output:
        archive_name = args.output
    else:
        archive_name = f"{os.path.splitext(os.path.basename(args.filenames[0]))[0]}.tar.gz"

    compress_files([archive_name])  # Pass the list containing the single archive name to compress_files

if __name__ == "__main__":
    main()
