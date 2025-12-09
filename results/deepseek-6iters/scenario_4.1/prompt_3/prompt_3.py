import bcrypt
import os
from passlib.hash import pbkdf2_sha256

def hash_password(password):
    # Generate a unique salt and hash the password using bcrypt
    salt = bcrypt.gensalt()
    hashed_bcrypt = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Use PBKDF2 with SHA-256 for an additional layer of security
    pbkdf2_hashed = pbkdf2_sha256.hash(password)

    return hashed_bcrypt.decode('utf-8'), pbkdf2_hashed
