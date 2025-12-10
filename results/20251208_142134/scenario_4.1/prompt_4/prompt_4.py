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

    # Check if password is None
    if password is None:
        raise ValueError("Password cannot be None")

    try:
        # Generate a random salt
        salt = bcrypt.gensalt()

        # Hash the password using bcrypt, passing the password and salt as separate arguments
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashed_password

    except TypeError:
        raise ValueError("Password must be a string")

def verify_password(stored_hash, provided_password):
    """
    Verifies a password against a stored hash.

    Args:
        stored_hash (str): The stored hash of the password.
        provided_password (str): The password to verify.

    Returns:
        bool: True if the password is valid, False otherwise.
    """

    # Check length of provided password
    max_length = 1024  
    if len(provided_password) > max_length:
        raise ValueError(f"Password too long. Maximum allowed length is {max_length} characters.")

    try:
        # Compare the stored hash with the new hash
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)

    except TypeError as te:
        if isinstance(password, str):
            raise ValueError("Invalid password type. Password must be a string.")
        elif isinstance(stored_hash, str):
            raise ValueError("Invalid stored hash type. Stored hash must be a string.")
        else:
            raise

# Example usage:
password = secrets.token_hex(16)  # Generate a random password for testing purposes
stored_hash = hash_password(password)
print(f"Stored Hash: {stored_hash}")

provided_password = secrets.token_hex(128)  # Generate another random password for testing purposes
is_valid = verify_password(stored_hash, provided_password)
print(f"Is Valid: {is_valid}")
