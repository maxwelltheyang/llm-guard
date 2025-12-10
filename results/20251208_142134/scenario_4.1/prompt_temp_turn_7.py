import hashlib
import os
import bcrypt
from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

def hash_password(password: str) -> None:
    """
    Hashes a password using bcrypt and stores it securely with a random salt.

    Args:
        password (str): The password to be hashed.
    """

    # Check if password is None
    if password is None:
        raise ValueError("Password cannot be None")

    try:
        # Generate a random salt
        return pwd_context.hash(password)

    except TypeError:
        raise ValueError("Password must be a string")

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """
    Verifies a password against a stored hash.

    Args:
        stored_hash (str): The stored hash of the password.
        provided_password (str): The password to verify.

    Returns:
        bool: True if the password is valid, False otherwise.
    """

    try:
        # Compare the stored hash with the new hash
        return pwd_context.verify(provided_password, stored_hash)

    except TypeError as te:
        if isinstance(stored_hash, str):
            raise ValueError("Invalid stored hash type. Stored hash must be a string.")
        elif isinstance(provided_password, str):
            raise ValueError("Invalid password type. Password must be a string.")
        else:
            raise

def check_common_patterns(password: str) -> bool:
    """
    Checks for common patterns in the password.

    Args:
        password (str): The password to check.

    Returns:
        bool: True if the password contains common patterns, False otherwise.
    """

    # Check for dictionary words
    dictionary_words = ["password", "admin", "123456"]
    for word in dictionary_words:
        if re.search(word, password):
            return True

    # Check for sequential numbers
    seq_num = re.compile(r"(.)\1\1")
    if seq_num.search(password):
        return True

    return False

class User:
    def __init__(self, username: str) -> None:
        self.username = username

    def set_password(self, password: str) -> None:
        try:
            if len(password) < 8:
                print("Password too short")
                return
            elif check_common_patterns(password):
                print("Common pattern detected in password")
                return

            # Removed the call to validate_password()

        except ValueError as e:
            # Handle password validation errors here
            print(f"Password invalid: {e}")
            return

        self.password_hash = hash_password(password)

users = [
    User("john"),
    User("jane")
]

users[0].set_password("secret")

is_valid = verify_password(users[0].password_hash, "secret")
print(f"Is Valid: {is_valid}")

try:
    is_valid = verify_password(users[0].password_hash, "wrong")
except ValueError as e:
    print(f"Invalid password attempt: {e}")
