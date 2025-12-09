import os
import bcrypt
from datetime import datetime, timedelta
import secrets

def hash_password(password):
    if len(password) < 8 or len(password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(input_password, stored_hash):
    if len(input_password) < 8 or len(input_password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")

    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash)

def enforce_password_expiry(days=90):
    if 'LAST_PASSWORD_CHANGE' in os.environ:
        last_change = datetime.strptime(os.getenv('LAST_PASSWORD_CHANGE'), '%Y-%m-%d')
        if datetime.now() > last_change + timedelta(days=days):
            return False, "Password has expired."
    return True, None  # Return a boolean and optionally a message

def generate_secret_key():
    return secrets.token_hex(32)  # Generates a 64-character hexadecimal string

# Example usage:
if __name__ == "__main__":
    password = os.getenv("PASSWORD", "default_password")  # Fallback to a default if not set
    hashed_pass = hash_password(password)
    print("Stored Hash:", hashed_pass)

    test_password = os.getenv("TEST_PASSWORD", "default_test_password")
    valid, message = enforce_password_expiry()
    if not valid:
        print(message)

    secret_key = generate_secret_key()
    print("Generated Secret Key:", secret_key)
