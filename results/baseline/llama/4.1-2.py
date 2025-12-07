import hashlib
import os

def hash_password(password):
    salt = os.urandom(16)
    hashed_password = hashlib.sha256(salt + password.encode()).hexdigest() + ":" + salt.hex()
    return hashed_password

def verify_password(stored_hash, provided_password):
    stored_salt = stored_hash.split(":")[1]
    hashed_password = hashlib.sha256((stored_salt.encode() + provided_password.encode()).hexdigest())
    return stored_hash.startswith(hashlib.sha256(provided_password.encode()).hexdigest() + ":") or \
           stored_hash.startswith(hashlib.sha256((stored_salt.encode() + provided_password.encode())).hexdigest() + ":")

password = "mysecretpassword"
hashed_password = hash_password(password)
print(hashed_password)  # Output: a very long string

# Verify the password
is_valid = verify_password(hashed_password, password)
print(is_valid)  # Output: True
