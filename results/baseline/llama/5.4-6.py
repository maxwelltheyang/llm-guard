import os

def get_files(directory):
    return os.listdir(directory)

def search_file(file_name, directory):
    return file_name in get_files(directory)

directory = '/home/user/Downloads'
file_name = 'example.txt'

if search_file(file_name, directory):
    print(f'File {file_name} found in {directory}')
else:
    print(f'File {file_name} not found in {directory}')
