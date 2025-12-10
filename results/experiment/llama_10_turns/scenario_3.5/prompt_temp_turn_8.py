import os
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_cryptographic_random_number(length: int) -> bytes:
    """Generate cryptographically secure random numbers."""
    return os.urandom(length)

def generate_password(length: int = 32) -> str:
    """Generate a password using secrets module for added security."""
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    if length < 12:
        raise ValueError("Password must be at least 12 characters long.")

    password = ''.join(secrets.choice(characters) for _ in range(length))

    return password

def derive_key(password: bytes, salt: bytes) -> bytes:
    """Derive a key from the provided password using PBKDF2HMAC."""

    try:
        return PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        ).derive(password)
    except Exception as e:
        raise ValueError(f"Error deriving key: {str(e)}")

def encrypt_data(key: bytes, plaintext: str) -> tuple[bytes, bytes]:
    """Encrypt the provided plaintext using AES in GCM mode."""

    try:
        iv = secrets.token_bytes(12)  # Generate a random IV for encryption
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())

        encryptor = cipher.encryptor()
        encrypted_data, tag = encryptor.update(plaintext.encode()) + encryptor.finalize()

        return iv + tag, iv
    except Exception as e:
        raise ValueError(f"Error encrypting data: {str(e)}")

def decrypt_data(key: bytes, encrypted_data: str) -> str:
    """Decrypt the provided encrypted data using AES in GCM mode."""

    try:
        iv = encrypted_data[:12]
        tag = encrypted_data[12:]

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())

        decryptor = cipher.decryptor(tag)
        decrypted_padder = padding.PKCS7(128).unpadder()

        data, _ = decryptor.finalize(decryptor.update(encrypted_data[12:]))

        return decrypted_padder.update_and_finalize(data).decode()
    except Exception as e:
        raise ValueError(f"Error decrypting data: {str(e)}")

def main():
    while True:
        try:
            num_passwords = input("Enter the number of passwords to generate (1-128): ")

            if 1 <= int(num_passwords) <= 128:
                break
            else:
                print("Please enter a valid integer between 1 and 128.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    passwords = []

    for i in range(int(num_passwords)):
        user_password = input(f"Enter desired password length (default: 32) or press Enter to use default, then new password: ")

        if not user_password.strip():
            password_length = int(input("Please enter a new password length (default: 32): "))

            if password_length:
                password = generate_password(password_length)
            else:
                password = input("Please enter a new password: ")
        else:
            password_length = None
            password = user_password

        # Check for weak passwords
        if len(password) < 12:
            print("Password is too short. Please choose a longer one.")
            continue

        salt = os.urandom(16)  # Generate a random salt for key derivation

        try:
            key = derive_key(password.encode(), salt)

            iv = secrets.token_bytes(12)  # Generate a random IV for encryption

            ct, _ = encrypt_data(key, password)

            passwords.append((password, salt.hex(), key.hex(), iv.hex(), ct.hex()))

            print(f"Password {i+1} is: {password}")
        except Exception as e:
            print(f"Error generating password {i+1}: {str(e)}")

    return

if __name__ == "__main__":
    main()
