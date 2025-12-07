import bcrypt
import os

def hash_password(password):
    # Generate a new salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Example usage
if __name__ == "__main__":
    password = "mysecretpassword"
    hashed_password = hash_password(password)
    print("Hashed Password:", hashed_password.decode('utf-8'))
