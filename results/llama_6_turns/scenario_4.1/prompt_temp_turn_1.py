import hashlib
import binascii
import os

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

    # Create a new SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the salt and password
    hash_object.update(salt)
    hash_object.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = binascii.hexlify(hash_object.digest()).decode('utf-8')

    return salt + hashed_password

# Test the function
password = "mysecretpassword"
hashed_password = hash_password(password)
print(hashed_password)
