import os

def check_input(user_input):
    if ".." in user_input:
        return False
    return True

# Example usage
user_input = input("Enter a directory: ")
if check_input(user_input):
    # Proceed with further operations
    pass
