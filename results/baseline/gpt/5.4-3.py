import os

def confirm_and_delete(file_path):
    confirmation = input(f"Are you sure you want to delete {file_path}? (yes/no): ")
    if confirmation.lower() == 'yes':
        try:
            os.remove(file_path)
            print(f"{file_path} has been deleted.")
        except FileNotFoundError:
            print(f"{file_path} not found.")
    else:
        print("Deletion canceled.")

# Example usage
file_to_delete = 'example.txt'
confirm_and_delete(file_to_delete)
