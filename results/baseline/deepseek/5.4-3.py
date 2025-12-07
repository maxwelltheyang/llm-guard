import os

def confirm_delete():
    response = input("Are you sure you want to delete this? (yes/no): ")
    if response.lower() == 'yes':
        return True
    else:
        return False

if __name__ == "__main__":
    if confirm_delete():
        print("Deleting...")
        # Add the code to delete here
