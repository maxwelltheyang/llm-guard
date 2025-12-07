import string
import secrets

def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        try:
            password = ''.join(secrets.choice(characters) for _ in range(length))
            return password
        except ValueError:
            continue  # If an exception occurs, try again with a new password

# Test the function
print(generate_password(12))
