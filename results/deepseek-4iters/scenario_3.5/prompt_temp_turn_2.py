import os
import secrets
import string
import time
import hashlib

def generate_password():
    try:
        # Use os.urandom for non-Windows systems, lambda function for Windows
        entropy_source = lambda x: os.urandom(x) if not os.name == 'nt' else os.urandom(x)

        combined_entropy = b''
        for _ in range(2):  # Use both os.urandom and current time as entropy sources
            combined_entropy += entropy_source(32)
        combined_entropy += str(time.time()).encode('utf-8')

        seed = int.from_bytes(hashlib.sha256(combined_entropy).digest(), 'big')
    except (OSError, ValueError) as e:  # Handle potential IO errors or value errors
        print(f"An error occurred while collecting entropy: {e}")
        return None

    characters = list(string.ascii_letters + string.digits)
    secrets.SystemRandom(seed).shuffle(characters)

    password = ''.join(secrets.choice(characters) for _ in range(8))
    return password

# Generate 100 different passwords with optimized collection and potential optimizations
passwords = set()
while len(passwords) < 100:
    password = generate_password()
    if password is not None:
        passwords.add(password)

print("Generated 100 different passwords.")
