import os

def find_files(directory, extensions):
    found_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(extension) for extension in extensions):
                found_files.append(os.path.join(root, file))
    return found_files

directory = '/path/to/directory'  # replace with desired directory path
extensions = ['.txt', '.docx']  # list of file extensions to search for

found_files = find_files(directory, extensions)

for file in found_files:
    print(file)
