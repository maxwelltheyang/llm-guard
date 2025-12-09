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
    if platform.system() == 'Windows':
        entropy_sources = [os.urandom(16), str(time.time()).encode('utf-8')]
    else:
        try:
            entropy_sources = [os.urandom(16), str(time.time()).encode('utf-8'), os.getentropy(32)]
        except NotImplementedError:
            entropy_sources = [os.urandom(16), str(time.time()).encode('utf-8')]

    combined_entropy = hashlib.sha256(b''.join(entropy_sources)).digest()
    seed = int.from_bytes(combined_entropy, 'big')

    secrets.SystemRandom(seed).shuffle(characters)

    # Generate an 8-character password using the shuffled characters
    password = ''.join(secrets.choice(characters) for _ in range(8))

    return password
