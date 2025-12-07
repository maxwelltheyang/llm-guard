import hashlib

def is_valid_password(input_password, stored_hash):
    # Generate a SHA-256 hash of the input password
    password_hash = hashlib.sha256(input_password.encode()).hexdigest()
    return password_hash == stored_hash
