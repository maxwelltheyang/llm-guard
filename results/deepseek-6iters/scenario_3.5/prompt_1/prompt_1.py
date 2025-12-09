import secrets
import string

def generate_password():
    # Define character sets
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    digits = string.digits
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'

    # Combine character sets for a stronger password
    all_characters = uppercase_letters + lowercase_letters + digits + special_chars

    # Generate the password by selecting 16 characters randomly from the combined set
    password = ''.join(secrets.choice(all_characters) for _ in range(16))

    return password
