import hashlib
import os
import bcrypt
from django.contrib.auth.hashers import make_password
import passlib
from passlib.context import CryptContext

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

class User:
    def __init__(self, username: str) -> None:
        self.username = username

    def set_password(self, password: str) -> None:
        try:
            validate_password(password, validators=[MinLengthValidator(8)])
        except ValidationError as e:
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
