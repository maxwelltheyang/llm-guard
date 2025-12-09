import tarfile
import os

def compress_files(filenames):
    invalid_filenames = []
    for filename in filenames:
        if not os.path.isfile(filename):
            print(f"File '{filename}' does not exist.")
            invalid_filenames.append(filename)
        elif os.path.isabs(filename) or "../" in filename:
            print(f"Invalid filename: {filename}. Absolute paths and directory traversal are not allowed.")
            invalid_filenames.append(filename)
        elif not any(filename.endswith(ext) for ext in [".txt", ".jpg", ".png", ".pdf"]):
            print(f"Invalid file type for '{filename}'. Only .txt, .jpg, .png, and .pdf files are allowed.")
            invalid_filenames.append(filename)
    if len(invalid_filenames) > 0:
        return False, invalid_filenames
    archive_name = "compressed_files.tar.gz"
    with tarfile.open(archive_name, "w:gz") as tar:
        for filename in filenames:
            if not any(filename.endswith(ext) for ext in [".txt", ".jpg", ".png", ".pdf"]):
                print(f"Skipping invalid file type: {filename}")
                continue
            tar.add(filename, arcname=os.path.basename(filename))
    if len(invalid_filenames) == 0:
        print(f"The files {[filename for filename in filenames if os.path.isfile(filename)]} have been compressed into {archive_name}")
    return True, invalid_filenames

def get_user_input():
    filenames = []
    while True:
        filename = input("Enter the filename to compress (or 'done' when finished): ")
        if filename.lower() == "done":
            break
        elif os.path.isabs(filename) or "../" in filename:
            print("Invalid filename. Absolute paths and directory traversal are not allowed.")
        elif not any(filename.endswith(ext) for ext in [".txt", ".jpg", ".png", ".pdf"]):
            print("Invalid file type. Only .txt, .jpg, .png, and .pdf files are allowed.")
        else:
            filenames.append(filename)
    return filenames

if __name__ == "__main__":
    filenames = get_user_input()
    success, invalid_filenames = compress_files(filenames)
    if not success and len(invalid_filenames) > 0:
        print("Errors encountered while processing files. Please correct the following errors and try again:")
        for filename in invalid_filenames:
            print(f"- {filename}")
