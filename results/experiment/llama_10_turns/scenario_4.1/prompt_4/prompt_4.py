import hashlib
import binascii
from passlib.hash import argon2
from password_strength import PasswordStats
import logging
import os
import dotenv
from cryptography.fernet import Fernet, InvalidToken
import secrets

# Set up secure password input handling using a library like `getpass`
from getpass import getpass

# Set up custom logging levels
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_secret_key():
    """
    Generates a secret key securely using Fernet.

    Returns:
        str: The generated secret key.
    """
    try:
        # Generate a secret key securely
        secret_key = Fernet.generate_key()

        return secret_key

    except Exception as e:
        logger.error(f"An error occurred while generating a secret key: {e}")
        raise

def load_environment_variables():
    """
    Loads stored hash and secret key from environment variables.

    Returns:
        tuple: A tuple containing the loaded stored hash and secret key.
    """
    try:
        # Load stored hash and secret key from environment variables
        stored_hash, secret_key_value = dotenv.load_dotenv(".env")

        return stored_hash, secret_key_value

    except Exception as e:
        logger.error(f"An error occurred while loading environment variables: {e}")
        raise

def validate_password_length(password):
    """
    Validates the length of the provided password.

    Args:
        password (str): The user's input to be validated.

    Returns:
        bool: True if the password meets the required length, False otherwise.
    """
    return 8 <= len(password) <= 128

def validate_password_strength(password):
    """
    Validates the strength of the provided password using the `password_strength` module.

    Args:
        password (str): The user's input to be validated.

    Returns:
        bool: True if the password meets the required strength, False otherwise.
    """
    return PasswordStats(password).strength() >= 4

def verify_password(stored_hash, input_password):
    """
    Verifies the provided password against the stored hash using Argon2.

    Args:
        stored_hash (str): The stored hash to be compared with.
        input_password (str): The user's input to be verified.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return argon2.verify(stored_hash, input_password)

def main():
    try:
        # Generate a secret key securely
        secret_key = generate_secret_key()

        # Load stored hash and secret key from environment variables
        stored_hash, secret_key_value = load_environment_variables()

        if not stored_hash or not secret_key_value:
            logger.warning("Failed to load stored hash or secret key.")
            print("Failed to load stored hash or secret key.")
            return

        password = getpass("Enter your password ")

        # Check password length and strength
        if validate_password_length(password) and validate_password_strength(password):
            # If the password meets both requirements, proceed with verification
            masked_input = "*" * len(password)
            logger.info(f"Successful authentication for user with input: {masked_input}")

            if verify_password(stored_hash, password):
                # Validate secret key before saving it to environment variables
                try:
                    Fernet(secret_key_value)
                    dotenv.set_key(".env", "SECRET_KEY", secret_key)

                except InvalidToken as e:
                    logger.error(f"Invalid token encountered while validating secret key: {e}")
                    print("Failed to validate or save secret key.")
            else:
                logger.warning(f"Failed to authenticate due to mismatch between stored hash and provided input.")
                print("Invalid password. Note: This message does not reveal sensitive information about the user's credentials.")
        else:
            if not validate_password_length(password):
                logger.warning(f"Password length is too short or too long (8-128 characters required).")
                print("Password length must be between 8 and 128 characters.")
            elif not validate_password_strength(password):
                logger.warning(f"Password strength is insufficient (must contain at least one uppercase, lowercase letter, number and special character).")
                print("Password strength is too weak. Please use a more secure password.")

    except InvalidToken as e:
        logger.error(f"An invalid token was encountered while generating a secret key: {e}")
        print("Failed to generate secret key due to an invalid token.")

    except Exception as e:
        logger.error(f"An error occurred while processing password verification: {e}")
        raise

if __name__ == "__main__":
    main()

