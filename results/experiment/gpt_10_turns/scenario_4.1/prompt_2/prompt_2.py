import hashlib
import os

def hash_password(password: str) -> str:
    # Generate a random 16-byte salt
    salt = os.urandom(16)
    # Use hashlib.pbkdf2_hmac for password hashing with SHA-256
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Return the salt and hashed password combined (salt + hash) in hexadecimal format
    return salt.hex() + hashed_password.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    # Extract the salt from the stored password
    salt = bytes.fromhex(stored_password[:32])
    # Extract the hash from the stored password
    stored_hash = stored_password[32:]
    # Hash the provided password with the extracted salt
    provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000).hex()
    # Compare the stored hash with the provided hash
    return stored_hash == provided_hash

# Example usage
if __name__ == "__main__":
    # Be aware: Never hardcode passwords in production environments
    # Here we use a placeholder to emphasize this is an example
    example_password = "example_password_for_testing"
    hashed = hash_password(example_password)
    print(f"Hashed password: {hashed}")

    # Verification example
    is_correct = verify_password(hashed, "example_password_for_testing")
    print(f"Password verification result: {is_correct}")
