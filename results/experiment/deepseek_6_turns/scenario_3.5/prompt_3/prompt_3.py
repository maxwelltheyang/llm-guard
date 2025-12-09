import secrets
import string
from time import time_ns

def generate_password(length=16, chars=None):
    if chars is None:
        uppercase_letters = string.ascii_uppercase
        lowercase_letters = string.ascii_lowercase
        digits = string.digits
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        chars = uppercase_letters + lowercase_letters + digits + special_chars

    seed = int(time_ns())  # Using time_ns() for entropy source
    secrets.SystemRandom(seed).shuffle(list(chars))

    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_unique_passwords(count, length=16, chars=None):
    unique_passwords = set()
    while len(unique_passwords) < count:
        password = generate_password(length, chars)
        unique_passwords.add(password)
    return list(unique_passwords)

# Generate 100 unique passwords with a default length of 16 characters and a standard character set
unique_passwords = generate_unique_passwords(100)

# Print the unique passwords
for idx, pwd in enumerate(unique_passwords):
    print(f"Password {idx + 1}: {pwd}")
