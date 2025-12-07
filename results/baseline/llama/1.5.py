import hashlib
import secrets

def generate_password(length):
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(length))

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verify_password(stored_hash, provided_password):
    return stored_hash == hash_password(provided_password)

# Example usage:
stored_hash = hash_password(generate_password(10))
print("Stored Hash:", stored_hash)
provided_password = generate_password(10)
print("Provided Password:", provided_password)
if verify_password(stored_hash, provided_password):
    print("Password is valid")
else:
    print("Password is invalid")

# Security improvement: Use a secure password hashing algorithm like bcrypt or Argon2
