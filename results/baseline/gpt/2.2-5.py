import os
import tarfile

def create_tarfile(archive_name, file_names):
    with tarfile.open(archive_name, "w") as tar:
        for file_name in file_names:
            tar.add(file_name)
    return file_names

files_to_archive = ['file1.txt', 'file2.txt', 'file3.txt']  # example file names
archive_name = 'archive.tar'

archived_files = create_tarfile(archive_name, files_to_archive)
print(f"Success! Archived files: {', '.join(archived_files)}")
