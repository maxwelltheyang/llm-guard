import bcrypt

def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(stored_hash, password):
    # Check the password
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# Example usage:
# hashed = hash_password('your_password')
# is_verified = verify_password(hashed, 'your_password')
