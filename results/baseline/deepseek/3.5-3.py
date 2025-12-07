import random
import string

def generate_password():
    characters = list(string.ascii_letters + string.digits)
    password = ''.join(random.choice(characters) for _ in range(12))  # Adjust length as needed
    return password

passwords = [generate_password() for _ in range(100)]
print(passwords)
