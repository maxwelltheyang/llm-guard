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
        raise ValueError("Length must be between 1 and 256.")

    # Check if the provided characters are safe and do not include any potentially harmful characters
    if re.search(r'[^a-zA-Z0-9!@#$%^&*()_+-=[]{}|;:,.<>?]', chars):
        raise ValueError("Invalid character set provided.")

    return True

def generate_passwords(num_passwords, length, chars):
    validate_input(length, chars)
    passwords = [generate_password(length, chars) for _ in range(num_passwords)]
    return passwords

# Example usage:
num_passwords = 5
length = 16
chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
passwords = generate_passwords(num_passwords, length, chars)
for idx, pwd in enumerate(passwords):
    print(f"Password {idx + 1}: {pwd}")
