import hashlib
import os
import bcrypt
import secrets

def hash_password(password):
    """
    Hashes a password using PBKDF2HMAC and stores it securely.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: A hashed password that can be stored in the database.
    """

    # Use bcrypt which handles storage of salt and hashed password securely
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Example usage:
password = secrets.token_hex(16)  # Generate a random password for testing purposes
hashed_password = hash_password(password)
print(f"Hashed Password: {hashed_password}")
