import hashlib

def hash_password(password):
    # Create a new SHA-256 hash object
    hash_object = hashlib.sha256()

    # Convert the password string into bytes and update the hash object
    hash_object.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = hash_object.hexdigest()

    return hashed_password

# Example usage:
password = "mysecretpassword"
hashed_password = hash_password(password)
print(hashed_password)
