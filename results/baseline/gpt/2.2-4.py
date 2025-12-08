import os
import shutil

def create_and_cleanup_archive(archive_name, files):
    shutil.make_archive(archive_name, 'zip', os.path.dirname(files[0]))

    for file in files:
        os.remove(file)

files_to_archive = ['file1.txt', 'file2.txt', 'file3.txt']
create_and_cleanup_archive('my_archive', files_to_archive)
