import os
import secrets
import string

def generate_password(length=16):
    try:
        with open('/dev/urandom', 'rb') as random_file:
            random_bytes = random_file.read(length)
            return ''.join(format(x, '08x') for x in random_bytes)[:length]
    except IOError:
        # If there's an error reading from /dev/urandom, fall back to the secrets module
        password = []
        while len(password) < length:
            try:
                char = secrets.choice(string.ascii_letters + string.digits)
                if char not in password:  # Ensure uniqueness
                    password.append(char)
            except Exception as e:
                print(f"Error generating password: {e}")

        return ''.join(password)

def main():
    passwords = [generate_password() for _ in range(100)]

    for i, password in enumerate(passwords):
        print(f"Password {i+1}: {password}")

if __name__ == "__main__":
    main()
