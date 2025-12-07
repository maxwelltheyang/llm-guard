import secrets
import string

def generate_password(length):
    all_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(all_characters) for _ in range(length))

# Test the function
print(generate_password(12))
