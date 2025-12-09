import bcrypt
import getpass  # Importing the module to securely obtain user input

def hash_password(password):
    # Generate a salt and hash the password using bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Function to securely obtain user input for password
def get_user_input():
    password = getpass.getpass("Please enter your password: ")
    return password

# Example usage:
if __name__ == "__main__":
    password = get_user_input()  # Securely obtain the password from the user
    hashed_pass = hash_password(password)
    print("Hashed Password:", hashed_pass.decode('utf-8'))
