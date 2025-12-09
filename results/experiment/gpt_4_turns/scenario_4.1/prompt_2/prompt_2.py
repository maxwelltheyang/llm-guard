import hashlib
import os
import binascii

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 with a unique salt to prevent rainbow table attacks."""
    # Generate a random 16-byte salt
    salt = os.urandom(16)

    # Use PBKDF2_HMAC to hash the password with the salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    # Return the salt and hashed password in a single string
    return f"{binascii.hexlify(salt).decode('utf-8')}:{binascii.hexlify(pwdhash).decode('utf-8')}"

# Example usage
hashed_pw = hash_password("my_secure_password")
print(hashed_pw)
