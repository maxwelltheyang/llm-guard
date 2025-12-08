import os
import random

def secure_random():
    return int(os.urandom(4).hex(), 16)

# Example usage:
secure_value = secure_random()
print(secure_value)
