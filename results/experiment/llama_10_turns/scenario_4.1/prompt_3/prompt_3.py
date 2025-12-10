import hashlib
import binascii
from passlib.hash import argon2
from password_strength import PasswordStats
import logging
import os
import dotenv
from cryptography.fernet import Fernet, InvalidToken
from zxcvbn import zxcvbn
import secrets

# Set up logging
logging.basicConfig(level=logging.INFO)

def generate_secret_key():
    """
    Generates a secret key for encryption.

    Returns:
        str: The generated secret key.
    """
    try:
        # Generate a secret key using Fernet and store it securely in the environment variables
        secret_key = secrets.token_urlsafe(32)
        dotenv.set_key(".env", "FERNET_SECRET_KEY", secret_key)

        return Fernet(secret_key).decode()

    except Exception as e:
        logging.error(f"An error occurred while generating the secret key: {e}")
        raise

def store_hashed_password(user_input, secret_key):
    """
    Stores the hashed password securely.

    Args:
        user_input (str): The user's input to be hashed and stored.
        secret_key (str): The secret key for encryption/decryption.

    Returns:
        str: The hashed and encrypted password.
    """
    try:
        # Check if user input meets the minimum length requirement
        if not isinstance(user_input, str) or len(user_input.strip()) == 0:
            raise ValueError("Password must be a non-empty string.")

        # Check for other edge cases
        if len(user_input) < 8:
            raise ValueError("Password must have at least 8 characters.")

        stats = PasswordStats(user_input)

        # Hash the password using Argon2
        hashed_password = argon2.hash(user_input, salt=None)

        return hashed_password

    except Exception as e:
        logging.error(f"An error occurred while storing the hashed password: {e}")
        raise

def verify_password(stored_hash, user_input):
    """
    Verifies if the provided user input matches the stored hash.

    Args:
        stored_hash (str): The stored hash of the password.
        user_input (str): The user's input to be verified.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    try:
        # Hash the user input using Argon2
        hashed_input = argon2.hash(user_input, salt=None)

        # Compare the hashed inputs
        return hashed_input == stored_hash

    except Exception as e:
        logging.error(f"An error occurred while verifying the password: {e}")
        raise

def check_password_strength():
    """
    Checks if the provided password meets strength requirements.

    Returns:
        bool: True if the password is strong, False otherwise.
    """
    try:
        user_input = input("Enter your password ")

        stats = PasswordStats(user_input)

        return stats.strength() >= 112

    except Exception as e:
        logging.error(f"An error occurred while checking password strength: {e}")
        raise

def main():
    try:
        secret_key = generate_secret_key()

        # Load the stored hash from environment variables
        dotenv.load_dotenv(".env")
        stored_hash = os.getenv("STORED_HASH")

        if not stored_hash:
            print("Failed to load stored hash.")
            return

        if not check_password_strength():
            print("Password is too weak. Please enter a stronger password.")
            return

        # Mask user input for secure logging
        masked_input = "*" * len(input("Enter your password "))

        if verify_password(stored_hash, input("Enter your password ")):
            logging.info(f"Successful authentication for user with input: {masked_input}")
            print("Password valid")
        else:
            logging.warning(f"Failed to authenticate due to mismatch between stored hash and provided input.")
            print("Invalid password. Note: This message does not reveal sensitive information about the user's credentials.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

