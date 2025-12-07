def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Some processing on the content...
            return content
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        return None
    except PermissionError:
        print(f"Error: You do not have permission to access the file {file_path}.")
        return None
    except Exception as e:
        print(f"An error occurred while processing the file {file_path}: {str(e)}")
        return None

def main():
    file_path = input("Enter a file path: ")
    content = process_file(file_path)
    if content is not None:
        # Further processing on the content...
        pass

if __name__ == "__main__":
    main()
