import hashlib
import binascii
from passlib.hash import pbkdf2_sha256 as hash
from password_strength import PasswordStats
from cryptography.fernet import Fernet
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR)

def generate_secret_key():
    """
    Generates a secret key for encryption.

    Returns:
        str: The generated secret key.
    """
    try:
        # Generate a secret key using Fernet
        return Fernet.generate_key().decode()
    except Exception as e:
        logging.error(f"An error occurred while generating the secret key: {e}")
        raise

def store_hashed_password(user_input, secret_key):
    """
    Stores the hashed password securely.

    Args:
        user_input (str): The user's input.
        secret_key (str): The secret key for encryption.

    Returns:
        str: The encrypted hash of the user's input.
    """
    try:
        # Hash the user's input
        hashed_password = hash.hash(user_input)

        # Store the hashed password securely
        cipher_suite = Fernet(secret_key)
        return cipher_suite.encrypt(hashed_password.encode()).decode()
    except Exception as e:
        logging.error(f"An error occurred while storing the hashed password: {e}")
        raise

def verify_password(stored_hash, user_input):
    """
    Verifies a password using the stored hash.

    Args:
        stored_hash (str): The encrypted hash of the user's input.
        user_input (str): The user's input.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    try:
        # Decrypt the stored hash
        cipher_suite = Fernet(os.environ['SECRET_KEY'])
        decrypted_stored_hash = cipher_suite.decrypt(stored_hash.encode()).decode()

        # Compare the hashed password in plaintext with the user's input
        return hash.verify(user_input, decrypted_stored_hash)
    except Exception as e:
        logging.error(f"An error occurred while verifying the password: {e}")
        raise

def check_password_strength(user_input):
    """
    Checks if a password meets certain strength criteria.

    Args:
        user_input (str): The user's input.

    Returns:
        bool: True if the password is strong, False otherwise.
    """
    try:
        # Calculate password statistics
        stats = PasswordStats(user_input)

        # Check length
        if len(user_input) < 8:
            return False

        # Check for repeated characters
        if '***' in str(stats.repeated):
            return False

        # If all checks pass, the password is strong
        return True
    except Exception as e:
        logging.error(f"An error occurred while checking the password strength: {e}")
        raise

def main():
    try:
        secret_key = generate_secret_key()

        attempts = 0
        max_attempts = 5

        while attempts < max_attempts:
            user_input = input("Enter your password (attempt {} of {}): ".format(attempts + 1, max_attempts))

            # Check password strength
            if not check_password_strength(user_input):
                print("Password is too weak. Please try again.")
                continue

            stored_hash = store_hashed_password(user_input, secret_key)

            is_valid = verify_password(stored_hash, user_input)

            if is_valid:
                print("Password valid")  # Should print: Password valid
                break

            attempts += 1

        if attempts == max_attempts:
            logging.error(f"Maximum number of attempts exceeded. Authentication failed.")

    except Exception as e:
        logging.error(f"An error occurred while verifying the password: {e}")

if __name__ == "__main__":
    main()

