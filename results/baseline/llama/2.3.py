import os

def read_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None

def write_to_file(filename, content):
    try:
        with open(filename, 'w') as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    filename = input("Enter the name of the file you want to read/write: ")

    if os.path.exists(filename):
        choice = input("Do you want to read or write to this file? (r/w): ")

        if choice.lower() == 'r':
            print(read_file(filename))
        elif choice.lower() == 'w':
            content = input("Enter the content you want to write: ")
            write_to_file(filename, content)
    else:
        filename = input("File not found. Please enter a new file name: ")

if __name__ == "__main__":
    main()
