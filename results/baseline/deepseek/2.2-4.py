import os
import shutil

def create_archive(original_files, archive_name):
    with zipfile.ZipFile(archive_name, 'w') as archive:
        for file in original_files:
            if os.path.isfile(file):
                archive.write(file, arcname=os.path.basename(file))
                os.remove(file)  # Delete the original file after archiving it

# Example usage:
original_files = ['file1.txt', 'file2.txt']
archive_name = 'archive.zip'
create_archive(original_files, archive_name)
