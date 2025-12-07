import os

def get_random_bytes(n):
    return os.urandom(n)

# Example usage:
random_string = ''.join(format(x, '02x') for x in get_random_bytes(16))
print(random_string)
