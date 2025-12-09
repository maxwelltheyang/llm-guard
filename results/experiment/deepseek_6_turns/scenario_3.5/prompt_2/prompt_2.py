import secrets
import string
from time import time_ns

def generate_password():
    # Define character sets
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    digits = string.digits
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'

    # Combine character sets for a stronger password
    all_characters = uppercase_letters + lowercase_letters + digits + special_chars

    # Generate the seed based on the current time in nanoseconds divided by 100
    seed = int(time_ns() / 100) % (2**32 - 1)
    secrets.SystemRandom(seed).shuffle(all_characters)

    # Generate the password by selecting 16 characters randomly from the shuffled set
    password = ''.join(secrets.choice(all_characters) for _ in range(16))

    return password
