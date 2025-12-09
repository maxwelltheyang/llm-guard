import bcrypt
import re

def hash_password(password, salt=None):
    if salt is None:
        # Generate a new salt and use it to hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    else:
        # Use the provided salt to hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(stored_hash, input_password):
    # Compare the input password with the stored hash without hardcoding passwords
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))

# Example usage:
if __name__ == "__main__":
    password = "mysecretpassword"
    # Automatically generate a new salt for each password hash
    hashed_password = hash_password(password)
    print("Hashed Password:", hashed_password)

    while True:
        test_password = input("Enter your password: ")  # Prompt user for input instead of hardcoding
        if len(test_password) < 8 or not re.search(r'[A-Z]', test_password) or not re.search(r'[a-z]', test_password) or not re.search(r'\d', test_password) or not re.search(r'[^a-zA-Z\d]', test_password):
            print("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
        else:
            break

    if check_password(hashed_password, test_password):
        print("Password matches the stored hash.")
    else:
        print("Password does not match the stored hash.")
