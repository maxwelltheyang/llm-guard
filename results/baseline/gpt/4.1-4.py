import hashlib

def verify_password(stored_password_hash, salt, password_attempt):
    hash_attempt = hashlib.pbkdf2_hmac(
        'sha256',
        password_attempt.encode('utf-8'),
        salt,
        100000
    )
    return hash_attempt == stored_password_hash
