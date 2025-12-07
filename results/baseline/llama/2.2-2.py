import zipfile
from pathlib import Path

def create_archive(filename, *filenames):
    with zipfile.ZipFile(filename, 'w') as zip_file:
        for filename_in_archive in filenames:
            file_path = Path(filename_in_archive)
            if file_path.is_dir():
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        file_path_in_archive = f"{root.replace(str(file_path), '')}/{file}"
                        zip_file.write(os.path.join(root, file), arcname=file_path_in_archive)
            else:
                zip_file.write(filename_in_archive)

# Example usage
create_archive('example.zip', 'path/to/file1.txt', 'path/to/directory')
