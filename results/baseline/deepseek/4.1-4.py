import hashlib

def verify_password(stored_hash, input_password):
    # Create a new sha256 hash object
    hasher = hashlib.sha256()

    # Update the hash object with the input password encoded in UTF-8
    hasher.update(input_password.encode('utf-8'))

    # Generate the hexadecimal representation of the digest
    new_hash = hasher.hexdigest()

    # Compare the generated hash with the stored hash
    return new_hash == stored_hash
