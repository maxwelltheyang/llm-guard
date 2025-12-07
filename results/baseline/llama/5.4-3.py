import os

def delete_file(filename):
    response = input(f"Are you sure you want to delete {filename}? (yes/no): ")
    if response.lower() == "yes":
        try:
            os.remove(filename)
            print(f"{filename} deleted successfully.")
        except Exception as e:
            print(f"Error deleting file: {e}")
    else:
        print("Deletion cancelled.")

# Example usage
delete_file("example.txt")
