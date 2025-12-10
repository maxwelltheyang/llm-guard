import os
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Define string constants for alphanumeric characters and digits
string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def generate_cryptographic_random_number(length):
    """Generate cryptographically secure random numbers."""
    return os.urandom(length)

def generate_password(length):
    """Generate a password using secrets module for added security."""
    characters = string
    password = ''.join(secrets.choice(characters) for _ in range(length))

    return password

def derive_key(password, salt):
    """Derive a key from the given password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000000,
        backend=default_backend()
    )

    return kdf.derive(password)

def encrypt_data(key, iv):
    """Encrypt some data (e.g., a password) using the derived key and IV."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Generate a random nonce for GCM mode
    nonce = os.urandom(12)

    # Pad the data before encryption (required for GCM mode)
    padder = padding.PKCS7(algorithms.AES().block_size).padder()
    padded_data = padder.update(b'') + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize(nonce)

    return nonce, encrypted_data

def decrypt_data(key, iv, encrypted_data):
    """Decrypt the given encrypted data using the derived key and IV."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Extract the nonce from the encrypted data
    nonce = encrypted_data[:12]
    encrypted_data = encrypted_data[12:]

    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize(nonce)

    unpadder = padding.PKCS7(algorithms.AES().block_size).unpadder()
    data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return data

def main():
    # Validate input for the number of passwords to generate
    while True:
        try:
            num_passwords = int(input("Enter the number of passwords to generate (1-128): "))

            if 1 <= num_passwords <= 128:
                break
            else:
                print("Please enter a valid integer between 1 and 128.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    # Generate the specified number of passwords
    passwords = []

    for i in range(num_passwords):
        password = generate_password(32)
        salt = os.urandom(16)  # Generate a random salt for key derivation

        try:
            key = derive_key(password.encode(), salt)
            iv = secrets.token_bytes(12)  # Generate a random IV for encryption

            nonce, encrypted_data = encrypt_data(key, iv)

            passwords.append((password, salt, key, iv, nonce, encrypted_data))

            print(f"Password {i+1} is: {password}")
        except Exception as e:
            print(f"Error generating password {i+1}: {str(e)}")

    return

if __name__ == "__main__":
    main()
