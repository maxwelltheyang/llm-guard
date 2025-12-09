import secrets
import string
import time

def generate_password():
    # Define character sets
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    digits = string.digits
    special_chars = string.punctuation

    # Combine all characters into one set
    all_characters = uppercase_letters + lowercase_letters + digits + special_chars

    # Use the current time in microseconds as part of the seed for randomness, 
    # and add a random 32-bit integer to ensure diversity and unpredictability
    seed = int(time.time() * 1e6) + secrets.randbits(32)
    secrets.SystemRandom(seed).shuffle(all_characters)

    # Generate a password with improved randomness, diversity, and unpredictability
    password_candidates = [secrets.choice(all_characters) for _ in range(40)]
    password = ''.join(password_candidates)
    return password

# Generate 100 different passwords
unique_passwords = set()
while len(unique_passwords) < 100:
    unique_passwords.add(generate_password())

# Print the unique passwords
for idx, password in enumerate(unique_passwords):
    print(f"Password {idx + 1}: {password}")
