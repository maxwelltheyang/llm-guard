import os
import hashlib
import binascii

def hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return binascii.hexlify(salt).decode() + binascii.hexlify(dk).decode()

def verify_password(stored_password: str, provided_password: str) -> bool:
    salt = binascii.unhexlify(stored_password[:32])
    stored_hash = stored_password[32:]
    dk = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
    return binascii.hexlify(dk).decode() == stored_hash
