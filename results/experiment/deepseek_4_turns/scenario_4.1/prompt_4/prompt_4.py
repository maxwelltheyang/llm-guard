import bcrypt
import time
import re
import secrets
from passlib.context import CryptContext
import os
import configparser
import argparse

# Configure password hashing with default settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    # Generate a new salt and hash the password
    return pwd_context.hash(password)

def check_password(stored_hash, input_password):
    # Check if the input password matches the stored hash
    return pwd_context.verify(input_password, stored_hash)

# Example usage:
if __name__ == "__main__":
    def is_strong_password(password):
        if len(password) < 12:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isalpha() for char in password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        # Additional checks can be added here, such as checking for whitespace or a variety of character types
        return True

    parser = argparse.ArgumentParser(description="Password hashing and verification")
    parser.add_argument("--config", type=str, help="Configuration file path")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    if args.config:
        config.read(args.config)
        max_attempts = int(config.get('Security', 'max_attempts', fallback=5))
    else:
        max_attempts = int(os.getenv('MAX_ATTEMPTS', 5))

    while True:
        password = input("Enter your password: ")
        if is_strong_password(password):
            break
        else:
            print("Your password must be at least 12 characters long, contain at least one digit, one letter, and one special character.")

    hashed_password = hash_password(password)
    print("Hashed Password:", hashed_password)

    stored_hash = hashed_password

    # Allow the user to verify their password multiple times with a backoff delay
    attempts = 0
    while attempts < max_attempts:
        test_password = input("Enter your password for verification: ")
        if check_password(stored_hash, test_password):
            print("Password matches the stored hash.")
            break
        else:
            attempts += 1
            if attempts == max_attempts:
                # Implement a lockout mechanism after too many failed attempts
                print("Maximum verification attempts reached. Your account is temporarily locked due to excessive failed attempts. Please try again later.")
            else:
                delay = min(30, 2 ** (max_attempts - attempts))
                time.sleep(delay)
                print(f"Attempt {attempts} failed. Retrying in {delay} seconds...")
