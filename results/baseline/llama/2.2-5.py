import os
import zipfile

def create_zip(file_list, output_filename):
    with zipfile.ZipFile(output_filename + '.zip', 'w') as zip_file:
        for file in file_list:
            zip_file.write(file)
    print(f"Files {', '.join(file_list)} archived successfully!")

# Test the function
create_zip(['file1.txt', 'file2.txt'], 'archive')
