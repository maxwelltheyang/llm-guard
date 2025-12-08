import os
from zipfile import ZipFile

def archive_files(directory, output_zip):
    with ZipFile(output_zip, 'w') as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                zipf.write(filepath, os.path.relpath(filepath, directory))
    print("Successfully archived the following files:", ', '.join([os.path.basename(file) for file in output_zip]))

# Example usage:
archive_files('path/to/directory', 'output.zip')
