import os
import bcrypt
from datetime import datetime, timedelta
import secrets

def hash_password(password):
    """Hashes a given password with a generated salt."""
    if len(password) < 8 or len(password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return (hashed_password, salt)

def verify_password(input_password, password_data):
    """Verifies if the input password matches the stored hash and salt."""
    if len(input_password) < 8 or len(input_password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")
    return bcrypt.checkpw(input_password.encode('utf-8'), password_data[0], password_data[1])

def enforce_password_expiry(user_passwords):
    """Checks if any passwords in the user_passwords dictionary have expired."""
    for user, (hashed_password, last_changed) in user_passwords.items():
        if last_changed is None or datetime.now() > last_changed + timedelta(days=90):
            yield f"{user}'s password has expired."
        else:
            yield f"{user}'s password is still valid."

def generate_secret_key():
    """Generates a secure secret key for the application."""
    return secrets.token_hex(32)  # Generates a 64-character hexadecimal string

# Example usage:
if __name__ == "__main__":
    users = {
        "user1": hash_password("password1"),
        "user2": hash_password("password2")
    }

    for message in enforce_password_expiry(users):
        print(message)

    secret_key = generate_secret_key()
    print("Generated Secret Key:", secret_key)
