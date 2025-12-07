import os

def secure_random_bytes(length):
    return os.urandom(length)
