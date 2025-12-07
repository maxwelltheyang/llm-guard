import os
import tarfile
from datetime import datetime
import tempfile
import shutil
import logging
from pathlib import Path

# Set up logging
logger = logging.getLogger('script_logger')
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def validate_path(path: Path) -> None:
    try:
        if not path.is_dir():
            raise ValueError(f"'{path}' is not a directory.")

        if not os.access(str(path), os.W_OK):
            raise PermissionError(f"No permission to write in '{str(path)}'.")

    except Exception as e:
        logger.error(f"An error occurred while validating the path: {str(e)}")

def compress_file(archive_path: Path, source_path: Path) -> None:
    try:
        # Validate and sanitize the archive path
        if not archive_path.is_absolute():
            raise ValueError("The archive path must be an absolute path.")

        sanitized_archive_path = str(archive_path.resolve())
        if not str(source_path).startswith(sanitized_archive_path):
            raise ValueError(f"Archive path '{sanitized_archive_path}' does not match source path '{str(source_path)}'.")

    except Exception as e:
        logger.error(f"An error occurred while validating the archive path: {str(e)}")

def main() -> None:
    try:
        # Extract command line arguments
        parser = argparse.ArgumentParser(description='Compress files into archives.')

        # Define the command line arguments
        parser.add_argument('filenames', nargs='+', help="One or more filenames to be compressed")

        args = parser.parse_args()

        # Extract the provided filenames
        filenames_to_compress = args.filenames

        if len(filenames_to_compress) == 0:
            raise ValueError("At least one filename must be provided.")

        # Sanitize and validate the filenames
        sanitized_filenames = []
        for file in filenames_to_compress:
            try:
                validate_filename(file)
                sanitized_filenames.append(sanitize_filename(file))

            except Exception as e:
                logger.error(f"An error occurred while sanitizing a filename: {str(e)}")

        if len(sanitized_filenames) == 0:
            raise ValueError("All filenames must be provided.")

        # Validate the paths
        temp_dir_path = Path(get_base_directory()) / 'temp'
        validate_path(temp_dir_path)

        with tempfile.TemporaryDirectory() as temp_dir_name:
            for file in sanitized_filenames:
                try:
                    source_path = Path(file)

                    # Validate that the source path exists and has write permissions.
                    validate_path(source_path)

                    # Create the archive
                    archive_path = Path(temp_dir_name) / f"{source_path.stem}.tar"
                    compress_file(archive_path, source_path)

                    logger.log_info(f"The file '{file}' has been successfully archived.")

                except Exception as e:
                    logger.error(f"An error occurred while processing a file: {str(e)}")

        logger.log_info("All files have been successfully archived.")

    except Exception as e:
        # Re-raise the exception to propagate it downstream.
        raise

if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        logger.error(f"An unexpected error occurred while executing the script: {str(e)}")
