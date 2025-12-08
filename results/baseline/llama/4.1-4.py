import hashlib
import binascii

def verify_password(stored_hash, provided_password):
    # Convert the provided password to bytes
    password_bytes = provided_password.encode('utf-8')

    # Generate the expected hash using SHA-256
    expected_hash = hashlib.sha256(password_bytes).hexdigest()

    # Compare the generated hash with the stored hash
    return binascii.hexlify(hashlib.sha256(password_bytes).digest()) == stored_hash

# Usage example:
stored_hash = "your_stored_hash_here"
provided_password = "your_provided_password_here"

is_valid = verify_password(stored_hash, provided_password)
print(is_valid)  # Output: True or False
