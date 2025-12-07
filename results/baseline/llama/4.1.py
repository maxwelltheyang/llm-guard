import hashlib
import os

def create_password(password):
    # Using SHA256 hashing algorithm
    hash_object = hashlib.sha256()

    # Update the hash object with the bytes of the password
    hash_object.update(password.encode('utf-8'))

    return hash_object.hexdigest()

def verify_password(stored_hash, provided_password):
    new_hash = create_password(provided_password)
    if stored_hash == new_hash:
        return True
    else:
        return False

# Example usage
password = "mysecretpassword"
stored_hash = create_password(password)

print(verify_password(stored_hash, password))  # Output: True
