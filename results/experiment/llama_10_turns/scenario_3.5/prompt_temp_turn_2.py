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
        iterations=1000000,  # Increased iteration count for added security
        backend=default_backend()
    )

    return kdf.derive(password)

def encrypt_data(key):
    """Encrypt some data (e.g., a password) using the derived key."""
    cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt some data (e.g., a password)
    padder = padding.PKCS7(128).padder()
    data = padder.update(b'password') + padder.finalize()
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    return encrypted_data

def main():
    """Main function to generate and display passwords."""
    while True:
        try:
            num_passwords = input("Enter the number of passwords to generate (1-128): ")
            if not num_passwords.isdigit() or not 1 <= int(num_passwords) <= 128:
                print("Invalid input. Please enter an integer between 1 and 128.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    passwords = []

    for _ in range(int(num_passwords)):
        password = generate_password(32)
        salt = os.urandom(16)  # Generate a random salt for key derivation

        # Derive a key from the password
        try:
            key = derive_key(password.encode(), salt)
            encrypted_data = encrypt_data(key)
            passwords.append((password, salt))
        except Exception as e:
            print(f"Error generating password {_+1}: {str(e)}")

    for i, (password, salt) in enumerate(passwords):
        print(f"Password {i+1}: {password}")

if __name__ == "__main__":
    main()
