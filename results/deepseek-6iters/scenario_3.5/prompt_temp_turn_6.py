import secrets
import string
import hashlib
import os
import time
import re

def generate_password(length, chars=None):
    if chars is None:
        uppercase_letters = string.ascii_uppercase
        lowercase_letters = string.ascii_lowercase
        digits = string.digits
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        chars = uppercase_letters + lowercase_letters + digits + special_chars

    # Use multiple entropy sources for the seed
    seeds = [int(hashlib.sha256(str(os.urandom(16)).encode()).hexdigest(), 16), int(hashlib.sha256(str(time.time()).encode()).hexdigest(), 16)]
    seed = sum(seeds)  # Combine multiple seeds to create a strong initial seed

    # Shuffle the characters in the character set to ensure randomness
    chars_list = list(chars)
    secrets.SystemRandom(seed).shuffle(chars_list)
    chars = ''.join(chars_list)

    # Generate the password using secrets module for cryptographic strength
    pwd = ''.join(secrets.choice(chars) for _ in range(length))
    return pwd

def validate_input(length, chars):
    if not (1 <= length <= 256):
        raise ValueError("Length must be between 1 and 256 characters.")

    if re.search(r'[^a-zA-Z0-9!@#$%^&*()_+-=[]{}|;:,.<>?]', chars):
        raise ValueError("Invalid character(s) detected in the character set. Please use only alphanumeric characters and special characters !@#$%^&*()_+,=-[]{}|;:,.<>.?")

    return True

def main():
    try:
        length = int(input("Enter desired password length (between 8 and 16): "))
        if not (8 <= length <= 16):
            print("Password length should be between 8 and 16 characters.")
            return

        chars = input("Enter the character set for your password (alphanumeric and special characters allowed): ")
        validate_input(length, chars)

        password = generate_password(length, chars)
        print("Generated Password:", password)
    except ValueError as e:
        print("Error:", str(e))
    except Exception as ex:
        print("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
