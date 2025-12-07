import hashlib
import binascii
import os
import secrets

def hash_password(password):
    """
    Hashes a password using SHA-256 and salts it with a random value.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: A SHA-256 hash of the password.
    """

    # Generate a cryptographically secure salt
    salt = os.urandom(16)

    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(password.encode('utf-8')).digest()

    # Combine the hash and salt into a single string, prefixed with the salt
    combined = binascii.hexlify(salt + hashed_password).decode('utf-8')

    return combined

# Example usage:
password_generator = secrets.SystemRandom()
random_password_length = password_generator.randint(1, 50)
random_password = ''.join(password_generator.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(random_password_length))
hashed_password = hash_password(random_password)
print(hashed_password)
