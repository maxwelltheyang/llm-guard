import bcrypt

def hash_password(password: str) -> str:
    """Hash a password for storage using bcrypt."""
    # Generate a salt and hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a hashed password against one provided by user."""
    # Check the provided password against the stored hashed password
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
