import os
import zipfile

def archive_files(file_names, archive_name):
    with zipfile.ZipFile(archive_name, 'w') as zipf:
        for file in file_names:
            if os.path.isfile(file):
                zipf.write(file)
    print(f"Success: Archived files: {', '.join(file_names)}")

file_list = ['file1.txt', 'file2.txt', 'file3.txt']
archive_name = 'archive.zip'
archive_files(file_list, archive_name)
