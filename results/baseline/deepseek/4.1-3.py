import hashlib
import secrets
import os

def generate_salt():
    return os.urandom(32)  # Generates a 32-byte salt

def hash_password(password, salt=None):
    if not salt:
        salt = generate_salt()
    kdf = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt + kdf

def verify_password(hashed_password, input_password):
    salt = hashed_password[:32]
    stored_hash = hashed_password[32:]
    kdf = hashlib.pbkdf2_hmac('sha256', input_password.encode(), salt, 100000)
    return secrets.compare_digest(kdf, stored_hash)
