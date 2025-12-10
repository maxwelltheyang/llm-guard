import os
import string
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_cryptographic_random_number(length):
    """Generate cryptographically secure random numbers."""
    return os.urandom(length)

def generate_password(length):
    """Generate a password with mixed character types."""
    characters = string.ascii_letters + string.digits
    password = ''.join(generate_cryptographic_random_number(1) for _ in range(length))

    # Replace some bytes with random characters from the allowed set
    for i, byte in enumerate(password):
        if (byte < 97 or byte > 122) and (byte < 65 or byte > 90) and (byte < 48 or byte > 57):
            password = password[:i] + chr(generate_cryptographic_random_number(1)[0]) + password[i+1:]

    return password

def derive_key(password, salt):
    """Derive a key from the given password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    return kdf.derive(password)

def main():
    """Main function to generate and display passwords."""
    num_passwords = input("Enter the number of passwords to generate: ")

    try:
        num_passwords = int(num_passwords)
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return

    if num_passwords < 1 or num_passwords > 128:
        print("Input is out of range. Please enter a value between 1 and 128.")
        return

    passwords = []

    for _ in range(num_passwords):
        password = generate_password(32)
        salt = os.urandom(16)

        # Derive a key from the password
        key = derive_key(password.encode(), salt)

        # Use the derived key to encrypt some data
        cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt some data (e.g., a password)
        padder = padding.PKCS7(128).padder()
        data = padder.update(b'password') + padder.finalize()
        encrypted_data = encryptor.update(data) + encryptor.finalize()

        passwords.append((password, salt))

    for i, (password, salt) in enumerate(passwords):
        print(f"Password {i+1}: {password}")

if __name__ == "__main__":
    main()
