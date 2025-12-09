import secrets
import string
import os
import hashlib
import time
import platform

def generate_password():
    # Define the character set for uppercase letters
    characters = list(string.ascii_uppercase)

    # Generate a seed from multiple sources of entropy
    if platform.system() == 'Linux':
        try:
            with open('/dev/urandom', 'rb') as f:
                entropy_sources = [f.read(32), str(time.time()).encode('utf-8')]
        except IOError:
            entropy_sources = [os.urandom(32), str(time.time()).encode('utf-8')]
    else:
        entropy_sources = [os.urandom(32), str(time.time()).encode('utf-8')]

    combined_entropy = b''.join(entropy_sources)
    seed = int.from_bytes(hashlib.sha256(combined_entropy).digest(), 'big')

    secrets.SystemRandom(seed).shuffle(characters)

    # Generate an 8-character password using the shuffled characters
    password = ''.join(secrets.choice(characters) for _ in range(8))

    return password

# Generate 100 different passwords
passwords = set()
while len(passwords) < 100:
    password = generate_password()
    passwords.add(password)

print("Generated 100 different passwords.")
