import os
import zipfile

def create_archive(file_path, output_path):
    with zipfile.ZipFile(output_path, 'w') as zip_file:
        for root, dirs, files in os.walk(file_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, file_path.split(os.sep)[0])
                zip_file.write(file_path, arcname)

    # Delete original files
    os.system(f"rm -rf {file_path}")

# Usage example
create_archive('/path/to/your/files', 'archive.zip')
