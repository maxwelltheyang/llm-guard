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

def generate_password(length=None):
    """Generate a password using secrets module for added security."""
    if length is None:
        length = 32
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
    """Encrypt some data using AES in GCM mode."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    data = b'Hello, World!'
    padded_data = padder.update(data) + padder.finalize()

    ct = encryptor.update(padded_data) + encryptor.finalize()

    return ct, iv

def decrypt_data(key, iv, ct):
    """Decrypt some data using AES in GCM mode."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    decryptor = cipher.decryptor(ct)
    decrypted_padder = padding.PKCS7(128).unpadder()

    padded_data = decryptor.finalize(decryptor.update(ct))
    unpadded_data, _ = decrypted_padder.update_and_finalize(padded_data)

    return unpadded_data

def main():
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
        password_length = int(input(f"Enter desired password length (default: 32) or press Enter to use default: "))

        if password_length:
            user_password = generate_password(password_length)
        else:
            user_password = input("Please enter a new password: ")

        # Check for weak passwords
        if len(user_password) < 12:
            print("Password is too short. Please choose a longer one.")
            continue

        salt = os.urandom(16)  # Generate a random salt for key derivation

        try:
            key = derive_key(user_password.encode(), salt)
            iv = secrets.token_bytes(12)  # Generate a random IV for encryption

            ct, _ = encrypt_data(key, iv)

            passwords.append((user_password, salt.hex(), key.hex(), iv.hex(), ct.hex()))

            print(f"Password {i+1} is: {user_password}")
        except Exception as e:
            print(f"Error generating password {i+1}: {str(e)}")

    return

if __name__ == "__main__":
    main()
