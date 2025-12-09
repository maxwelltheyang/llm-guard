import os
import bcrypt
from datetime import datetime, timedelta
import secrets

def hash_password(password):
    """
    Hashes the given password with a generated salt.

    Args:
        password (str): The user's password to be hashed.

    Returns:
        tuple: A tuple containing the hashed password and the salt used for hashing.
    """
    if len(password) < 8 or len(password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return (hashed_password, salt)

def verify_password(input_password, hashed_password_and_salt):
    """
    Verifies if the input password matches the stored hash and salt.

    Args:
        input_password (str): The password provided by the user for verification.
        hashed_password_and_salt (tuple): A tuple containing the hashed password and the original salt used for hashing.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    if len(input_password) < 8 or len(input_password) > 50:
        raise ValueError("Password must be between 8 and 50 characters long.")

    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password_and_salt[0], salt=hashed_password_and_salt[1])

def enforce_password_expiry(user_passwords):
    """
    Checks if any passwords in the user_passwords dictionary have expired.

    Args:
        user_passwords (dict): A dictionary containing usernames as keys and tuples of hashed password and last change timestamp as values.

    Yields:
        str: A message indicating whether a password is still valid or has expired.
    """
    for user, (hashed_password, last_changed) in user_passwords.items():
        if last_changed is None or datetime.now() > last_changed + timedelta(days=90):
            yield f"{user}'s password has expired."
        else:
            yield f"{user}'s password is still valid."

def generate_secret_key():
    """
    Generates a secure secret key for the application.

    Returns:
        str: A 64-character hexadecimal string representing the generated secret key.
    """
    secret_key = secrets.token_hex(32)
    print(f"Generated Secret Key: {secret_key}")
    return secret_key

# Example usage:
if __name__ == "__main__":
    # Test code here
    pass
