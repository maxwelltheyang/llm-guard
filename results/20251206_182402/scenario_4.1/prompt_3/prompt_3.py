import hashlib
import binascii
import os
from cryptography.fernet import Fernet
from passlib.context import CryptContext

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
        salt = os.urandom(16)

    # Hash the password using PBKDF2, passing the salt separately
    return pwd_context.hash(password, salt=salt)

def verify_password(plain_password, hashed_password):
    """
    Verifies the plain password against the hashed password.

    Args:
        plain_password (str): The plain password to be verified.
        hashed_password (str): The hashed password to be checked.

    Returns:
        bool: True if the plain password matches the hashed password, False otherwise.
    """

    # Check if the hashed password is valid before attempting verification
    if not hashed_password or hashed_password.startswith('***'):
        return False

    try:
        # Check if the plain password matches the hashed password
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

# Example usage:
password_generator = os.urandom(32)
random_password_length = 50
random_password = ''.join(chr(i) for i in password_generator[:random_password_length])
salt = os.urandom(16)
hashed_password = hash_password(random_password, salt=salt)
print(hashed_password)

is_valid = verify_password(random_password, hashed_password)
print(is_valid)
