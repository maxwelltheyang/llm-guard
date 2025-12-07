import tarfile

def create_tar(filenames, output_filename):
    with tarfile.open(output_filename, "w") as tar:
        for filename in filenames:
            tar.add(filename)

# Example usage
filenames = ["file1.txt", "file2.txt", "file3.txt"]
create_tar(filenames, "archive.tar")
