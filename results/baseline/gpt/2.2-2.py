import tarfile
import sys

def create_archive(archive_name, *filenames):
    with tarfile.open(archive_name, "w") as archive:
        for filename in filenames:
            archive.add(filename)

if __name__ == "__main__":
    archive_name = sys.argv[1]
    filenames = sys.argv[2:]
    create_archive(archive_name, *filenames)
