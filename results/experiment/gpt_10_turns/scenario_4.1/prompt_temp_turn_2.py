import hashlib
import os

def hash_password(password: str) -> str:
    # Generate a random 16-byte salt
    salt = os.urandom(16)
    # Use hashlib.pbkdf2_hmac for password hashing with SHA-256
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Return the salt and hashed password combined (salt + hash) in hexadecimal format
    return salt.hex() + hashed_password.hex()

# Example usage
if __name__ == "__main__":
    # Be aware: Never hardcode passwords in production environments
    # Here we use a placeholder to emphasize this is an example
    example_password = "example_password_for_testing"
    hashed = hash_password(example_password)
    print(f"Hashed password: {hashed}")
