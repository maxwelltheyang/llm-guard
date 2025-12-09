import bcrypt

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt, a strong password hashing function."""
    # Generate the salt and hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Return the hashed password as a decoded string for storage
    return hashed.decode('utf-8')

# Example usage
hashed_pw = hash_password("my_secure_password")
print(hashed_pw)
