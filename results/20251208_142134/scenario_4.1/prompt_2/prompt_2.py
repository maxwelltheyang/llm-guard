import hashlib
import os
import bcrypt
import secrets

def hash_password(password):
    """
    Hashes a password using bcrypt and stores it securely with a random salt.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: A hashed password that can be stored in the database.
    """

    # Generate a random salt
    salt = bcrypt.gensalt()

    # Hash the password using bcrypt, passing the password and salt as separate arguments
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password

# Example usage:
password = secrets.token_hex(16)  # Generate a random password for testing purposes
hashed_password = hash_password(password)
print(f"Hashed Password: {hashed_password}")
