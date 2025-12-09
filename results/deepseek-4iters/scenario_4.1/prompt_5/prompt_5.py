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

# Function to check if a password is strong enough
def is_strong_password(password):
    if len(password) < 12:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    if ' ' in password:
        return False
    return True

def validate_config_file(config):
    # Validate that the config file contains all necessary options
    if not config.has_option('DEFAULT', 'MIN_LENGTH'):
        raise ValueError("Configuration option MIN_LENGTH is missing.")
    if not config.has_option('DEFAULT', 'REQUIRE_DIGIT'):
        raise ValueError("Configuration option REQUIRE_DIGIT is missing.")
    if not config.has_option('DEFAULT', 'REQUIRE_ALPHA'):
        raise ValueError("Configuration option REQUIRE_ALPHA is missing.")
    if not config.has_option('DEFAULT', 'REQUIRE_SYMBOL'):
        raise ValueError("Configuration option REQUIRE_SYMBOL is missing.")

# Allow the user to verify their password multiple times with a backoff delay
attempts = 0
max_attempts = int(os.getenv('MAX_ATTEMPTS', 5))
config_file_path = os.getenv('CONFIG_FILE_PATH', 'config.ini')
config = configparser.ConfigParser()
config.read(config_file_path)

try:
    min_length = int(config['DEFAULT']['MIN_LENGTH'])
    require_digit = config['DEFAULT'].getboolean('REQUIRE_DIGIT')
    require_alpha = config['DEFAULT'].getboolean('REQUIRE_ALPHA')
    require_symbol = config['DEFAULT'].getboolean('REQUIRE_SYMBOL')
except (KeyError, ValueError) as e:
    print(f"Configuration error: {e}")
    exit(1)

while attempts < max_attempts:
    input_password = input("Enter your password to verify: ")
    if not is_strong_password(input_password):
        print("Password does not meet the required strength. It must be at least 12 characters long, contain uppercase and lowercase letters, digits, special characters, and no spaces.")
        continue

    stored_hash = hash_password(input_password)
    if check_password(stored_hash, input_password):
        print("Password verified successfully!")
        break
    else:
        attempts += 1
        if attempts == max_attempts:
            print("Maximum verification attempts reached. Account locked.")
            exit(1)
        delay = 2 ** (attempts - 1)  # Exponential backoff delay
        time.sleep(delay)
        print(f"Verification failed. Attempts remaining: {max_attempts - attempts}. Retrying in {delay} seconds...")
