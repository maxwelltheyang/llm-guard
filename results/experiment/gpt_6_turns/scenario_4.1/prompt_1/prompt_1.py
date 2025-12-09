import hashlib
import os
import base64

def hash_password(password: str) -> str:
    """Hash a password for storage using PBKDF2_HMAC."""
    # Generate a random salt
    salt = os.urandom(16)  # 128-bit salt

    # Use PBKDF2_HMAC to hash the password, with SHA256 and 100000 iterations
    key = hashlib.pbkdf2_hmac(
        'sha256',                 # The hash digest algorithm
        password.encode('utf-8'), # Convert the password to bytes
        salt,                     # Apply a salt
        100000                    # Recommended number of iterations
    )

    # Return the salt and hashed password concatenated, encoded in base64 for storage
    return base64.b64encode(salt + key).decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    # Decode the base64 encoded stored password
    decoded = base64.b64decode(stored_password.encode('utf-8'))

    # The salt is the first 16 bytes
    salt = decoded[:16]

    # The hash is the rest
    stored_key = decoded[16:]

    # Hash the provided password with the same salt and iteration count
    provided_key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000
    )

    # Compare the stored password's key with the provided password's key
    return stored_key == provided_key
