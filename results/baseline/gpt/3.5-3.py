import random
import string

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_passwords(count=100, length=12):
    passwords = set()
    while len(passwords) < count:
        passwords.add(generate_password(length))
    return list(passwords)

unique_passwords = generate_unique_passwords()

unique_passwords
