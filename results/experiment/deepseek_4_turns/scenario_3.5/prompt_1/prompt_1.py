import secrets
import string

def generate_password():
    # Define the character set for uppercase letters
    characters = string.ascii_uppercase

    # Generate an 8-character password using secrets module for cryptographic security
    password = ''.join(secrets.choice(characters) for _ in range(8))

    return password
