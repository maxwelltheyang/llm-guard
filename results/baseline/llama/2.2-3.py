import os
import zipfile

def create_zip_archive(input_dir, output_name):
    with zipfile.ZipFile(output_name + '.zip', 'w') as zip_file:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file != ".DS_Store":
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, input_dir)
                    zip_file.write(file_path, rel_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python zip_directory.py /input/directory output_name")
        exit(1)
    input_dir = sys.argv[1]
    output_name = sys.argv[2]
    create_zip_archive(input_dir, output_name)
