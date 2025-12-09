import bcrypt
import time

def hash_password(password):
    # Generate a new salt for each password hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8'), salt.decode('utf-8')  # Return the hash and salt as strings

def check_password(stored_hash, input_password):
    # Compare the input password with the stored hash
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))

# Example usage:
if __name__ == "__main__":
    def is_strong_password(password):
        return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

    # Get a strong password from the user (ensuring it meets the criteria)
    while True:
        password = input("Enter your password: ")
        if is_strong_password(password):
            break
        else:
            print("Password must be at least 8 characters long and contain at least one digit and one letter.")

    # Hash the user's password and display the hashed version and salt used
    hashed_password, salt = hash_password(password)
    print("Hashed Password:", hashed_password)
    print("Salt:", salt)

    stored_hash = hashed_password
    stored_salt = salt

    # Allow the user to verify their password multiple times with a backoff delay
    attempts = 0
    while True:
        test_password = input("Enter your password for verification: ")
        if check_password(stored_hash, test_password):
            print("Password matches the stored hash.")
            break
        else:
            print("Passwords do not match. Please try again.")
            attempts += 1
            time.sleep(min(attempts * 2, 30))  # Exponential backoff with a cap at 30 seconds
