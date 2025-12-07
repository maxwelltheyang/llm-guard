import hashlib
import binascii
import os
import secrets
from argon2 import PasswordHasher

def hash_password(password):
    """
    Hashes a password using Argon2 and salts it with a random value.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: An Argon2 hash of the password.
    """

    # Generate a cryptographically secure salt
    salt = os.urandom(16)

    # Hash the password using Argon2, passing the salt separately
    ph = PasswordHasher()
    hashed_password = ph.hash(password, salt=salt)

    return hashed_password

# Example usage:
password_generator = secrets.SystemRandom()
random_password_length = password_generator.randint(1, 50)
random_password = ''.join(password_generator.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(random_password_length))
hashed_password = hash_password(random_password)
print(hashed_password)
