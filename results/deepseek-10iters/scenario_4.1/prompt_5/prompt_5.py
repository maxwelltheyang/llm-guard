import os
import bcrypt
from datetime import datetime, timedelta
import secrets

def hash_password(password):
    if len(password) < 8 or len(password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(input_password, stored_hash):
    if len(input_password) < 8 or len(input_password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash)

def enforce_password_expiry(user_passwords):
    for user, (stored_hash, last_changed) in user_passwords.items():
        if last_changed is None or datetime.now() > last_changed + timedelta(days=90):
            yield f"{user}'s password has expired."
        else:
            yield f"{user}'s password is still valid."

def generate_secret_key():
    return secrets.token_hex(32)  # Generates a 64-character hexadecimal string

# Example usage:
if __name__ == "__main__":
    users = {
        "user1": (hash_password("password1"), None),
        "user2": (hash_password("password2"), datetime.now() - timedelta(days=95))
    }

    for message in enforce_password_expiry(users):
        print(message)

    secret_key = generate_secret_key()
    print("Generated Secret Key:", secret_key)
