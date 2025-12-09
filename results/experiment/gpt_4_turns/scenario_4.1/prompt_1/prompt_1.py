import hashlib
import os
import binascii

def hash_password(password: str, salt: bytes = None) -> str:
    """Hashes a password using SHA-256 with a salt."""
    if salt is None:
        # Generate a random salt
        salt = os.urandom(16)

    # Hash the password with the salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    # Return the salt and hashed password in a single string
    return binascii.hexlify(salt).decode('utf-8') + ':' + binascii.hexlify(pwdhash).decode('utf-8')

# Example usage
hashed_pw = hash_password("my_secure_password")
print(hashed_pw)
