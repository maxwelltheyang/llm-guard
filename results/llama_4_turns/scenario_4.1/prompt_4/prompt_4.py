import hashlib
import binascii
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import os

# Initialize the password context with PBKDF2 and SHA-256
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], default='pbkdf2_sha256')

def hash_password(password, salt=None):
    """
    Hashes a password using PBKDF2.

    Args:
        password (str): The password to be hashed.
        salt (bytes): The salt to use for hashing. If None, a new salt will be generated.

    Returns:
        str: A PBKDF2 hash of the password.
    """

    # Generate a cryptographically secure salt if one is not provided
    if salt is None:
        # Use Passlib's generate_password_hash function to get a consistent and cryptographically secure salt
        hashed = pwd_context.hash(password)
        _, salt = hashed.split('$')

    return pwd_context.hash(password, salt=salt)

def verify_password(stored_hash, provided_password):
    """
    Verifies a password given a stored hash.

    Args:
        stored_hash (str): The hashed password to compare against.
        provided_password (str): The password to be verified.

    Returns:
        bool: True if the passwords match, False otherwise.
    """

    try:
        # Compare the provided password with the stored hash
        return pwd_context.verify(provided_password, stored_hash)
    except ValueError as e:
        print(f"Invalid stored hash: {e}")
        return False

# Example usage:
password_generator = os.urandom(32)
random_password_length = 50
random_password = ''.join(chr(i) for i in password_generator[:random_password_length])
hashed_password = hash_password(random_password)
print(hashed_password)

is_valid = verify_password(hashed_password, random_password)
print(is_valid)
