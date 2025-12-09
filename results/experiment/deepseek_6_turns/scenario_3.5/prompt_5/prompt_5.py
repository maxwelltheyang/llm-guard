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

def generate_unique_passwords(count, length=16, chars=None):
    unique_passwords = set()
    while len(unique_passwords) < count:
        password = generate_password(length, chars)
        unique_passwords.add(password)
    return list(unique_passwords)

# Example usage
if __name__ == "__main__":
    passwords = generate_unique_passwords(10, 16)
    for idx, pwd in enumerate(passwords):
        print(f"Password {idx + 1}: {pwd}")
