import secrets
import string
import hashlib
import os
import time

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

    while True:
        try:
            secrets.SystemRandom(seed).shuffle(list(chars))
            break
        except (ValueError, TypeError):
            seed += 1

    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_unique_passwords(num_passwords, length, chars=None):
    passwords = []
    while len(passwords) < num_passwords:
        pwd = generate_password(length, chars)
        if pwd not in passwords:
            passwords.append(pwd)
    return passwords

# Example usage:
num_passwords = 5
length = 16
chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
passwords = generate_unique_passwords(num_passwords, length, chars)
for idx, pwd in enumerate(passwords):
    print(f"Password {idx + 1}: {pwd}")
